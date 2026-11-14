import sys
from core import fetch_subdomains, resolve_subdomain
from concurrency import dns_brute_forcing
from db import init_db, get_last_scan, save_scan, diff_scans

if len(sys.argv) > 2:
    print("too many argumants, only put one domain! ")
    sys.exit()

if len(sys.argv) == 1:
    try:
        base_domain = input("Enter a website: ").strip()
    except EOFError:
        sys.exit()
    if not base_domain:
        print("You did not enter a website")
        sys.exit()
else:
    base_domain = sys.argv[1]

sources = [
    (f"https://api.certspotter.com/v1/issuances?domain={base_domain}&include_subdomains=true&expand=dns_names", "CertSpotter"),
    (f"https://crt.sh/?q=%25.{base_domain}&output=json", "crt.sh"),
]

wildcard_probe = f"zzqxk92held.{base_domain}"
wildcard_ips = resolve_subdomain(wildcard_probe)

if wildcard_ips:
    print(f"Warning: wildcard DNS detected on {base_domain} (fake probe resolved to {wildcard_ips})")
else:
    print("No wildcard DNS detected.")

storage = dns_brute_forcing(base_domain, wildcard_ips)

web_data = None
for url, name in sources:
    web_data = fetch_subdomains(url, name)
    if web_data is not None:
        break

domain_set = set()
if web_data is None:
    print("Both CT sources failed. Showing DNS brute-force results only.")
elif web_data == []:
    print("No certificates found for this domain.")
else:
    for certificate in web_data:
        if "dns_names" in certificate:
            names = certificate.get("dns_names", [])
        else:
            names = str(certificate.get("name_value", "")).split("\n")
        for domain in names:
            if domain is not None and not domain.startswith("*."):
                domain_set.add(domain.lower())

domain_set.update(storage)

print(*sorted(domain_set), sep="\n")

conn = init_db()
if web_data is None:
    print("\nCT lookup failed, so this scan is incomplete: skipping diff and not saving it.")
else:
    previous = get_last_scan(conn, base_domain)
    if previous is None:
        print("\nFirst scan of this domain, nothing to compare against yet.")
    else:
        new, gone = diff_scans(previous, domain_set)
        print(f"\nNew since last scan ({len(new)}):")
        print(*sorted(new), sep="\n")
        print(f"\nGone since last scan ({len(gone)}):")
        print(*sorted(gone), sep="\n")
    save_scan(conn, base_domain, domain_set)
conn.close()