#!/usr/bin/env python3
"""ONVIF WS-Discovery for network cameras."""

import socket
import struct

ONVIF_DISCOVER_MSG = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
               xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery">
  <soap:Header>
    <wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>
    <wsa:MessageID>urn:uuid:cctv-hunter-probe</wsa:MessageID>
    <wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>
  </soap:Header>
  <soap:Body>
    <tns:Probe>
      <tns:Types>NetworkVideoTransmitter</tns:Types>
    </tns:Probe>
  </soap:Body>
</soap:Envelope>"""


def discover_onvif(timeout: float = 5.0) -> list[str]:
    """Send WS-Discovery probe and collect ONVIF device responses."""
    devices = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout)

    try:
        sock.sendto(ONVIF_DISCOVER_MSG.encode(), ("239.255.255.250", 3702))
        while True:
            try:
                data, addr = sock.recvfrom(65535)
                devices.append(addr[0])
            except socket.timeout:
                break
    finally:
        sock.close()

    return list(set(devices))
