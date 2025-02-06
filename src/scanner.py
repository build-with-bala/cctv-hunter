#!/usr/bin/env python3
"""CCTV Hunter - Network camera discovery tool."""

import argparse
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from fingerprint import fingerprint_device
from rtsp_probe import probe_rtsp
from reporter import generate_report

CCTV_PORTS = [554, 8554, 80, 8080, 443, 3702]


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


def scan_network(target: str, ports: list[int], threads: int = 100) -> list[dict]:
    if "/" in target:
        hosts = [str(ip) for ip in ipaddress.IPv4Network(target, strict=False).hosts()]
    else:
        hosts = [target]

    print(f"Scanning {len(hosts)} hosts on ports {ports}")
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_host, ip, ports): ip for ip in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results


def enrich_results(hosts: list[dict]) -> list[dict]:
    for host in hosts:
        fp = fingerprint_device(host["ip"], host["open_ports"])
        host.update(fp)
        if 554 in host["open_ports"] or 8554 in host["open_ports"]:
            rtsp_port = 554 if 554 in host["open_ports"] else 8554
            host["rtsp_streams"] = probe_rtsp(host["ip"], rtsp_port)
    return hosts


def main():
    parser = argparse.ArgumentParser(description="CCTV Hunter - Network camera discovery tool")
    parser.add_argument("--target", "-t", required=True, help="Target IP or CIDR range")
    parser.add_argument("--ports", "-p", default=None, help="Comma-separated ports")
    parser.add_argument("--threads", default=100, type=int)
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()

    ports = [int(p) for p in args.ports.split(",")] if args.ports else CCTV_PORTS
    hosts = scan_network(args.target, ports, args.threads)

    if not hosts:
        print("No cameras found.")
        sys.exit(0)

    hosts = enrich_results(hosts)

    for h in hosts:
        print(f"[+] {h['ip']} | Ports: {h['open_ports']} | Mfr: {h.get('manufacturer', '?')}")

    from datetime import datetime
    out = args.output or f"output/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    generate_report(hosts, out)
    print(f"\nReport: {out}")


if __name__ == "__main__":
    main()
