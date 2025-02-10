#!/usr/bin/env python3
"""Shared utilities."""

import ipaddress


def is_valid_target(target: str) -> bool:
    try:
        if "/" in target:
            ipaddress.IPv4Network(target, strict=False)
        else:
            ipaddress.IPv4Address(target)
        return True
    except ValueError:
        return False


def format_mac(mac: str) -> str:
    mac = mac.replace(":", "").replace("-", "").upper()
    return ":".join(mac[i:i+2] for i in range(0, 12, 2))
