#!/usr/bin/env python3
"""Device fingerprinting for discovered cameras."""

import re
import socket
import requests

MANUFACTURER_SIGNATURES = {
    "hikvision": ["hikvision", "hikvi", "DNVRS-Webs", "App-webs"],
    "dahua": ["dahua", "DH-", "DHIP"],
    "axis": ["axis", "AXIS"],
    "reolink": ["reolink"],
    "amcrest": ["amcrest"],
    "foscam": ["foscam"],
    "tp-link": ["tp-link", "tplink", "tapo"],
    "uniview": ["uniview", "UNV"],
    "vivotek": ["vivotek"],
    "bosch": ["bosch"],
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


def check_http(ip: str, port: int) -> dict:
    info = {"headers": {}, "title": "", "server": ""}
    try:
        resp = requests.get(f"http://{ip}:{port}/", timeout=3, verify=False, allow_redirects=True)
        info["headers"] = dict(resp.headers)
        info["server"] = resp.headers.get("Server", "")
        title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
        if title_match:
            info["title"] = title_match.group(1)
        info["body_snippet"] = resp.text[:500]
    except requests.RequestException:
        pass
    return info


def identify_manufacturer(banner: str, http_info: dict) -> str:
    combined = " ".join([
        banner.lower(),
        http_info.get("server", "").lower(),
        http_info.get("title", "").lower(),
        http_info.get("body_snippet", "").lower(),
    ])
    for manufacturer, signatures in MANUFACTURER_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in combined:
                return manufacturer
    return "Unknown"


def fingerprint_device(ip: str, open_ports: list[int]) -> dict:
    result = {"manufacturer": "Unknown", "model": "Unknown", "firmware": "Unknown", "banners": {}}
    http_info = {}
    for port in open_ports:
        banner = grab_banner(ip, port)
        if banner:
            result["banners"][port] = banner[:200]
        if port in [80, 8080, 443, 8000, 9000]:
            http_info = check_http(ip, port)
    result["manufacturer"] = identify_manufacturer(" ".join(result["banners"].values()), http_info)
    return result
