#!/usr/bin/env python3
"""RTSP stream discovery for IP cameras."""

import socket

COMMON_RTSP_PATHS = [
    "/",
    "/live",
    "/stream1",
    "/Streaming/Channels/101",
    "/cam/realmonitor",
    "/h264Preview_01_main",
]


def probe_rtsp(ip: str, port: int = 554, timeout: float = 3.0) -> list[str]:
    valid_streams = []
    for path in COMMON_RTSP_PATHS:
        uri = f"rtsp://{ip}:{port}{path}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            req = f"DESCRIBE {uri} RTSP/1.0\r\nCSeq: 1\r\n\r\n"
            sock.send(req.encode())
            resp = sock.recv(4096).decode("utf-8", errors="ignore")
            sock.close()
            if "200 OK" in resp:
                valid_streams.append(uri)
            elif "401" in resp:
                valid_streams.append(f"{uri} (auth required)")
        except (socket.error, OSError):
            continue
    return valid_streams
