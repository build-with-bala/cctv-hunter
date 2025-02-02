#!/usr/bin/env python3
"""Device fingerprinting for discovered cameras."""

import socket
import requests

MANUFACTURER_SIGNATURES = {
    "hikvision": ["hikvision", "DNVRS-Webs"],
    "dahua": ["dahua", "DH-"],
    "axis": ["axis", "AXIS"],
}


def grab_banner(ip: str, port: int, timeout: float = 2.0) -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.send(b"GET / HTTP/1.0\r\nHost: %b\r\n\r\n" % ip.encode())
        banner = sock.recv(4096).decode("utf-8", errors="ignore")
        sock.close()
        return banner
    except (socket.error, OSError):
        return ""


def fingerprint_device(ip: str, open_ports: list[int]) -> dict:
    result = {"manufacturer": "Unknown", "model": "Unknown", "banners": {}}
    for port in open_ports:
        banner = grab_banner(ip, port)
        if banner:
            result["banners"][port] = banner[:200]
            for mfr, sigs in MANUFACTURER_SIGNATURES.items():
                if any(s.lower() in banner.lower() for s in sigs):
                    result["manufacturer"] = mfr
    return result
