import sys
from core import fetch_subdomains, resolve_subdomain
from concurrency import dns_brute_forcing


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

certspotter_url = f"https://api.certspotter.com/v1/issuances?domain={base_domain}&include_subdomains=true&expand=dns_names"
crtsh_url = f"https://crt.sh/?q=%25.{base_domain}&output=json"

wildcard_probe = f"zzqxk92held.{base_domain}"
wildcard_ips = resolve_subdomain(wildcard_probe)

if wildcard_ips:
    print(f"Warning: wildcard DNS detected on {base_domain} (fake probe resolved to {wildcard_ips})")
else:
    print("No wildcard DNS detected.")

storage = {

}

storage = dns_brute_forcing(base_domain, wildcard_ips)

web_data = fetch_subdomains(certspotter_url, "CertSpotter")
if web_data is None:
     print("Both sources failed. Exiting.")
else:
    domain_set = set()
    if web_data == []:
        print("No certificates found for this domain.")

    else:
        for certificate in web_data:
            if "dns_names" in certificate:
                for domain in certificate.get("dns_names", []):
                    if domain is not None and not domain.startswith("*."):
                        domain_set.add(domain)

            else:
                name_value = certificate.get("name_value", "")
                for domain in str(name_value).split("\n"):
                    if domain is not None and not domain.startswith("*."):
                        domain_set.add(domain)

    for candidate, result in storage.items():
        if result is not None:
            domain_set.add(candidate)

    print(*domain_set, sep="\n")
