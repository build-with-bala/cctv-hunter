#!/usr/bin/env python3
"""RTSP stream discovery for IP cameras."""

import socket

COMMON_RTSP_PATHS = [
    "/",
    "/live",
    "/live/ch00_0",
    "/cam/realmonitor",
    "/h264Preview_01_main",
    "/Streaming/Channels/101",
    "/Streaming/Channels/102",
    "/stream1",
    "/stream2",
    "/video1",
    "/videoMain",
    "/MediaInput/h264",
    "/media/video1",
    "/onvif1",
    "/onvif2",
    "/user=admin&password=&channel=1&stream=0.sdp",
    "/11",
    "/12",
]


def probe_rtsp(ip: str, port: int = 554, timeout: float = 3.0) -> list[str]:
    valid_streams = []
    for path in COMMON_RTSP_PATHS:
        uri = f"rtsp://{ip}:{port}{path}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            describe_req = (
                f"DESCRIBE {uri} RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"User-Agent: CCTVHunter/1.0\r\n"
                f"Accept: application/sdp\r\n"
                f"\r\n"
            )
            sock.send(describe_req.encode())
            response = sock.recv(4096).decode("utf-8", errors="ignore")
            sock.close()
            if "200 OK" in response:
                valid_streams.append(uri)
            elif "401" in response:
                valid_streams.append(f"{uri} (auth required)")
        except (socket.error, OSError):
            continue
    return valid_streams
