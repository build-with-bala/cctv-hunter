#!/usr/bin/env python3
"""CCTV Hunter - Network camera discovery tool."""

import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

CCTV_PORTS = [554, 8554, 80, 8080, 443]


def scan_host(ip: str, ports: list[int], timeout: float = 1.5) -> dict | None:
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except (socket.error, OSError):
            continue
    if open_ports:
        return {"ip": ip, "open_ports": open_ports}
    return None


def main():
    parser = argparse.ArgumentParser(description="CCTV Hunter")
    parser.add_argument("--target", "-t", required=True)
    parser.add_argument("--ports", "-p", default=None)
    args = parser.parse_args()

    import ipaddress
    if "/" in args.target:
        hosts = [str(ip) for ip in ipaddress.IPv4Network(args.target, strict=False).hosts()]
    else:
        hosts = [args.target]

    ports = [int(p) for p in args.ports.split(",")] if args.ports else CCTV_PORTS

    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_host, ip, ports): ip for ip in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                print(f"[+] {result['ip']}: ports {result['open_ports']}")

    print(f"\nFound {len(results)} potential cameras")


if __name__ == "__main__":
    main()
