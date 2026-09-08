# Subrecon

A passive subdomain reconnaissance tool for discovering subdomains through Certificate Transparency (CT) log queries.

## Overview

subrecon identifies subdomains by querying public Certificate Transparency logs. Every HTTPS certificate issued by a Certificate Authority is permanently logged in CT logs—including certificates [...]

## Features

- **Passive CT log queries** — discovers subdomains through public certificate logs without sending traffic to target systems
- **Multiple data sources** — queries CertSpotter API with automatic fallback to crt.sh if the primary source is unavailable
- **Retry logic** — automatically retries failed requests up to 3 times before falling back to alternative sources
- **Wildcard filtering** — excludes wildcard certificate entries (e.g., `*.example.com`) since they don't represent resolvable hosts
- **Deduplication** — returns a clean, unique list of subdomains (the same subdomain often appears across multiple certificates)
- **Lightweight** — Python CLI tool with only `requests` library as a dependency; no database or external services required

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/asadullah85/Personal-recon-tool.git
   cd Personal-recon-tool
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

## Usage

Run subrecon against a domain:
```bash
python subrecon.py example.com
```

The tool will query CT logs and output a deduplicated list of discovered subdomains.

## Project Status

This is an early-stage learning and portfolio project under active development. Current release supports passive CT log lookup only. Planned features for future versions include:
- Active DNS brute-forcing
- Concurrent requests for improved performance
- Host fingerprinting and service detection

## Disclaimer

**Authorization Required:** This tool should only be used against:
- Domains you own
- Domains where you have explicit written permission to perform testing (e.g., published bug bounty program scope)

While Certificate Transparency lookups are passive and non-invasive, always respect responsible disclosure practices and obtain proper authorization before conducting any security reconnaissance. [...]

## License

MIT License

Copyright (c) 2026 asadullah85

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
