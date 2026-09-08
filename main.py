import requests
import time
import sys


if len(sys.argv) == 1:
    print("You did not enter a website! ")
    sys.exit()

if len(sys.argv) > 2:
    print("too many argumants, only put one domain! ")
    sys.exit()

base_domain = sys.argv[1]
headers = {"User-Agent": "Mozilla/5.0"}

def fetch_subdomains(url, source_name):
    for attempt in range(1, 4):
        try:
            response= requests.get(url, headers=headers, timeout=20)
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
                    print(f"Sorry, but the API response is not valid JSON: {json_err}") # Error handling for a failed JSON response

        except requests.exceptions.RequestException as e: # adds error handling for exceptions that aren't recognized
            print(f"{source_name}: sorry but the request itself has failed: {e}")

    return None

certspotter_url = f"https://api.certspotter.com/v1/issuances?domain={base_domain}&include_subdomains=true&expand=dns_names"
crtsh_url = f"https://crt.sh/?q=%25.{base_domain}&output=json"

web_data = fetch_subdomains(certspotter_url, "CertSpotter")

if web_data is None:
    print("Both sources failed. Exiting.")

else:
    domain_set = set()

    if web_data == []:
        print("No certificates found for this domain.")

    else:
        # Classify each certificate by its own shape instead of inspecting web_data[0].
        for certificate in web_data:
            if "dns_names" in certificate:  # CertSpotter shape for this certificate
                for domain in certificate.get("dns_names", []):
                    if domain is not None and not domain.startswith("*."):
                        domain_set.add(domain)

            else:  # fallback (crt.sh shape: name_value, newline-separated)
                name_value = certificate.get("name_value", "")
                for domain in str(name_value).split("\n"):
                    if domain is not None and not domain.startswith("*."):
                        domain_set.add(domain)

        print(*domain_set, sep="\n")