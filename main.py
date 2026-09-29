import requests
import time
import sys
import dns.resolver
from prefix import prefixes_list


if len(sys.argv) == 1: 
    print("You did not enter a website")
    sys.exit()

if len(sys.argv) > 2:
   print("too many argumants, only put one domain! ")
   sys.exit()

base_domain =   sys.argv[1] 

headers = {"User-Agent": "Mozilla/5.0"}

def fetch_subdomains(url, source_name):
    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                print(f"{source_name} succeeded with {response.status_code}")
                return response.json()

            if response.status_code in (500, 502, 503, 429):
                print(f"{source_name}: error getting a valid response, we'll try again")
                time.sleep(2)
                print(f"{source_name}: attempt {attempt} has failed, retrying")

                if attempt == 3:
                    print(f"{source_name}: all attempts have failed :(")
            else:
                print(f"{source_name}: failure code not recognized: {response.status_code}")
                return None

        except requests.exceptions.JSONDecodeError as json_err:
                    print(f"Sorry, but the API response is not valid JSON: {json_err}")

        except requests.exceptions.RequestException as e:
            print(f"{source_name}: sorry but the request itself has failed: {e}")

    return None

certspotter_url = f"https://api.certspotter.com/v1/issuances?domain={base_domain}&include_subdomains=true&expand=dns_names"
crtsh_url = f"https://crt.sh/?q=%25.{base_domain}&output=json"


def resolve_subdomain(candidate):
        try:
            answers = dns.resolver.resolve(candidate, 'A')
            return [answer.to_text() for answer in answers]
        except dns.resolver.NXDOMAIN:
            return None 
        except dns.resolver.NoNameservers: 
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.Timeout:
            print("failed to receive a response in time")

# --- WILDCARD DETECTION (new) ---
wildcard_probe = f"zzqxk92held.{base_domain}"
wildcard_ips = resolve_subdomain(wildcard_probe)

if wildcard_ips:
    print(f"Warning: wildcard DNS detected on {base_domain} (fake probe resolved to {wildcard_ips})")
else:
    print("No wildcard DNS detected.")

storage = {}

for prefix in prefixes_list:
    candidate = f"{prefix}.{base_domain}"
    result = resolve_subdomain(candidate)

    if wildcard_ips and result == wildcard_ips:
        continue

    storage[candidate] = result
    if result:
        print(f"{candidate} -> {result}")
   
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