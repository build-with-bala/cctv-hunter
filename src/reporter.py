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
        },
        "devices": hosts,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
