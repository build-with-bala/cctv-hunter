#!/usr/bin/env python3
"""Report generation for scan results."""

import json
from datetime import datetime
from pathlib import Path


def generate_report(hosts: list[dict], output_path: str):
    report = {
        "scan_info": {
            "timestamp": datetime.now().isoformat(),
            "total_cameras_found": len(hosts),
            "tool": "CCTV Hunter v1.0",
        },
        "devices": [],
    }
    for host in hosts:
        device = {
            "ip": host["ip"],
            "open_ports": host["open_ports"],
            "manufacturer": host.get("manufacturer", "Unknown"),
            "model": host.get("model", "Unknown"),
            "firmware": host.get("firmware", "Unknown"),
            "rtsp_streams": host.get("rtsp_streams", []),
            "default_creds_status": host.get("default_creds_status", "not_checked"),
        }
        report["devices"].append(device)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
