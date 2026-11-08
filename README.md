# Subrecon

A subdomain reconnaissance CLI tool that combines passive Certificate Transparency (CT) log discovery with active DNS brute-forcing.

## Overview

subrecon finds subdomains in two ways:

- **Passive:** it queries public Certificate Transparency logs. Every HTTPS certificate issued by a Certificate Authority is permanently logged, including certificates that may reveal subdomain names before they are publicly announced.
- **Active:** it resolves a wordlist of common subdomain prefixes against the target, filtering out wildcard DNS false positives.

Results from both methods are merged into one deduplicated list.

## Features

**Passive discovery**
- **CT log queries:** discovers subdomains through public certificate logs without sending traffic to the target
- **Multiple data sources:** queries the CertSpotter API, with automatic fallback to crt.sh if the primary source is unavailable
- **Retry logic:** retries failed requests up to 3 times before giving up on a source
- **Wildcard certificate filtering:** excludes entries like `*.example.com`, since they don't represent resolvable hosts
- **Deduplication:** the same subdomain often appears across many certificates, so results are returned as a unique set

**Active discovery**
- **DNS brute-forcing:** resolves a built-in wordlist of common prefixes (`www`, `mail`, `api`, ...) against the target
- **Wildcard DNS detection:** resolves a random nonexistent name first; any candidate that resolves to the same IP is discarded as a false positive
- **Concurrent resolution:** DNS lookups run in parallel via a thread pool for faster scans

**General**
- **Lightweight:** Python CLI with two dependencies (`requests`, `dnspython`); no database or external services required

## Installation

1. Clone the repository:

```
git clone https://github.com/asadullah85/Personal-recon-tool.git
cd Personal-recon-tool
```

2. Install dependencies:

```
pip install requests dnspython
```

## Usage

```
python main.py example.com
```

The tool checks for wildcard DNS, runs the DNS brute-force, queries CT logs, and prints a merged, deduplicated list of discovered subdomains.

## Project Status

This is an early-stage portfolio project under active development. The current version supports passive CT log lookup and active DNS brute-forcing with concurrent resolution.

Planned: host fingerprinting and service detection.

## Disclaimer

**Authorization required:** only use this tool against:

- Domains you own
- Domains where you have explicit written permission to test (e.g., published bug bounty program scope)

CT log lookups are passive, but the DNS brute-force sends queries for names under the target domain. Always respect responsible disclosure practices and get proper authorization before doing any security reconnaissance. Use outside authorized scope may violate laws and regulations.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/asadullah85/Personal-recon-tool/blob/main/LICENSE) file for details.
