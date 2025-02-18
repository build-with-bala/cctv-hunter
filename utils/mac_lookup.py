#!/usr/bin/env python3
"""MAC address vendor lookup."""

import subprocess
import re


def get_mac_from_arp(ip: str) -> str | None:
    """Get MAC address from ARP table."""
    try:
        output = subprocess.check_output(["arp", "-n", ip], text=True, timeout=5)
        match = re.search(r"([\da-fA-F]{1,2}[:-]){5}[\da-fA-F]{1,2}", output)
        return match.group(0) if match else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


# Common camera OUI prefixes
CAMERA_OUI = {
    "00:40:8C": "Axis Communications",
    "00:80:F0": "Panasonic",
    "28:57:BE": "Hangzhou Hikvision",
    "44:19:B6": "Hangzhou Hikvision",
    "54:C4:15": "Hangzhou Hikvision",
    "A4:14:37": "Zhejiang Dahua",
    "3C:EF:8C": "Zhejiang Dahua",
    "E0:50:8B": "Zhejiang Uniview",
    "9C:8E:CD": "Amcrest",
    "EC:71:DB": "Reolink",
}


def lookup_vendor(mac: str) -> str:
    """Lookup vendor from MAC OUI prefix."""
    prefix = mac.upper()[:8]
    return CAMERA_OUI.get(prefix, "Unknown")
