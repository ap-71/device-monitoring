import logging
from pysnmp.hlapi import *


class SnmpExService:
    _log = None

    def __init__(self):
        self._log = logging.getLogger(__name__)

    def snmp_getcmd(self, community, ip, port, OID):
        return (getCmd(SnmpEngine(),
                       CommunityData(community),
                       UdpTransportTarget((ip, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity(OID))))

    def snmp_get_next(self, community, ip, port, OID):
        errorIndication, errorStatus, errorIndex, varBinds = next(self.snmp_getcmd(community, ip, port, OID))
        for name, val in varBinds:
            return (val.prettyPrint())

    def exec_snmp(self, ip_address, port, community, oid) -> str:
        response = (self.snmp_get_next(community, ip_address, port, oid))
        self._log.debug("Device %s. Response %s" % (ip_address, str(response)))
        return response
