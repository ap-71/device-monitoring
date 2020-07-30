import logging
import os

from pysnmp.hlapi import *


class SnmpExService:
    _log = None

    def __init__(self):
        self._log = logging.getLogger(__name__)

    def snmp_bulkcmd(self, community, ip, port, OID):
        return (bulkCmd(SnmpEngine(),
                        CommunityData(community, mpModel=0),
                        UdpTransportTarget((ip, port)),
                        ContextData(),
                        0, 20,
                        ObjectType(ObjectIdentity(OID))))

    def snmp_getcmd(self, community, ip, port, OID):
        return (getCmd(SnmpEngine(),
                       CommunityData(community, mpModel=0),
                       UdpTransportTarget((ip, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity(OID))))

    def snmp_get_next(self, community, ip, port, OID, each=False):
        if not each:
            errorIndication, errorStatus, errorIndex, varBinds = next(self.snmp_getcmd(community, ip, port, OID))
        else:
            errorIndication, errorStatus, errorIndex, varBinds = next(self.snmp_bulkcmd(community, ip, port, OID))
        for name, val in varBinds:
            return val.prettyPrint()

    def exec_snmp(self, ip_address, port, community, oid, each=False) -> str:
        if not each:
            response = self.snmp_get_next(community, ip_address, port, oid)
        else:
            response = self.snmp_get_next(community, ip_address, port, oid, True)
        self._log.debug("Device %s. Response %s" % (ip_address, str(response)))
        return str(response)
