#!/usr/bin/env python3
"""CCTV Hunter - Network camera discovery tool."""

import argparse
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from fingerprint import fingerprint_device
from rtsp_probe import probe_rtsp
from reporter import generate_report

console = Console()

CCTV_PORTS = [554, 8554, 80, 8080, 443, 3702, 37777, 34567, 9000, 8000]


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

    console.print(f"\n[bold cyan]Scanning {len(hosts)} hosts on ports {ports}[/bold cyan]\n")
    results = []
    with Progress() as progress:
        task = progress.add_task("[green]Scanning...", total=len(hosts))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(scan_host, ip, ports): ip for ip in hosts}
            for future in as_completed(futures):
                progress.advance(task)
                result = future.result()
                if result:
                    results.append(result)
    return results


def enrich_results(hosts: list[dict], check_defaults: bool = False) -> list[dict]:
    console.print(f"\n[bold yellow]Fingerprinting {len(hosts)} hosts...[/bold yellow]\n")
    for host in hosts:
        fp = fingerprint_device(host["ip"], host["open_ports"])
        host.update(fp)
        if 554 in host["open_ports"] or 8554 in host["open_ports"]:
            rtsp_port = 554 if 554 in host["open_ports"] else 8554
            host["rtsp_streams"] = probe_rtsp(host["ip"], rtsp_port)
        if check_defaults:
            host["default_creds_status"] = "checked"
    return hosts


def display_results(hosts: list[dict]):
    if not hosts:
        console.print("\n[bold red]No CCTV cameras found.[/bold red]")
        return
    table = Table(title="Discovered CCTV Cameras", show_lines=True)
    table.add_column("IP Address", style="cyan", no_wrap=True)
    table.add_column("Open Ports", style="green")
    table.add_column("Manufacturer", style="yellow")
    table.add_column("Model", style="white")
    table.add_column("RTSP Streams", style="magenta")
    for host in hosts:
        ports_str = ", ".join(str(p) for p in host["open_ports"])
        manufacturer = host.get("manufacturer", "Unknown")
        model = host.get("model", "Unknown")
        streams = host.get("rtsp_streams", [])
        streams_str = "\n".join(streams) if streams else "N/A"
        table.add_row(host["ip"], ports_str, manufacturer, model, streams_str)
    console.print(table)
    console.print(f"\n[bold green]Total cameras found: {len(hosts)}[/bold green]")


def main():
    parser = argparse.ArgumentParser(
        description="CCTV Hunter - Network camera discovery tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--target", "-t", required=True, help="Target IP or CIDR range")
    parser.add_argument("--ports", "-p", default=None, help="Comma-separated ports")
    parser.add_argument("--threads", default=100, type=int, help="Scan threads")
    parser.add_argument("--check-defaults", action="store_true", help="Check default credentials")
    parser.add_argument("--output", "-o", default=None, help="Output file (JSON)")
    parser.add_argument("--timeout", default=1.5, type=float, help="Socket timeout")
    args = parser.parse_args()

    from banner import BANNER
    console.print(f"[bold red]{BANNER}[/bold red]")
    console.print("[dim]Network CCTV Camera Discovery Tool[/dim]\n")

    ports = [int(p) for p in args.ports.split(",")] if args.ports else CCTV_PORTS
    hosts = scan_network(args.target, ports, args.threads)

    if not hosts:
        console.print("\n[bold red]No hosts with open CCTV ports found.[/bold red]")
        sys.exit(0)

    console.print(f"\n[bold green]Found {len(hosts)} potential cameras[/bold green]")
    hosts = enrich_results(hosts, args.check_defaults)
    display_results(hosts)

    out = args.output or f"output/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    generate_report(hosts, out)
    console.print(f"\n[bold cyan]Report saved to: {out}[/bold cyan]")


if __name__ == "__main__":
    main()
