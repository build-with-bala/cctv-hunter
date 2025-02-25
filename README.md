# CCTV Hunter

Network CCTV camera discovery and security assessment tool for hackathon use.

## Features

- Network scanning to discover IP cameras
- CCTV-specific port detection (RTSP, HTTP, ONVIF)
- Default credential checking
- Device fingerprinting (manufacturer, model, firmware)
- RTSP stream discovery
- Report generation

## Disclaimer

**For authorized security testing and educational purposes only.** Only use on networks you own or have explicit written permission to test.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scan your local network
python src/scanner.py --target 192.168.1.0/24

# Scan with credential check
python src/scanner.py --target 192.168.1.0/24 --check-defaults

# Scan specific ports
python src/scanner.py --target 192.168.1.0/24 --ports 554,8554,80,8080
```

## Common CCTV Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 554  | RTSP     | Real Time Streaming Protocol |
| 8554 | RTSP     | Alternate RTSP |
| 80   | HTTP     | Web interface |
| 8080 | HTTP     | Alternate web interface |
| 443  | HTTPS    | Secure web interface |
| 3702 | WS-Discovery | ONVIF device discovery |
| 37777| TCP      | Dahua proprietary |
| 34567| TCP      | Generic DVR/NVR |

## Project Structure

```
cctv-hunter/
├── src/
│   ├── scanner.py        # Main network scanner
│   ├── fingerprint.py    # Device fingerprinting
│   ├── rtsp_probe.py     # RTSP stream discovery
│   ├── reporter.py       # Report generation
│   └── banner.py         # CLI banner
├── utils/
│   └── helpers.py        # Shared utilities
├── wordlists/
│   └── default_creds.json # Known default credentials
├── output/               # Scan results
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.
