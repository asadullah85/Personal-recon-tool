import requests
import time

base_domain = input("Type in your website: ")
domain_certspotter = f"https://api.certspotter.com/v1/issuances?domain={base_domain}&include_subdomains=true&expand=dns_names"

headers = {"User-Agent": "Mozilla/5.0"}

for attempt in range(1, 4):
    try:
        response = requests.get(domain_certspotter, headers=headers, timeout=20)
        if response.status_code == 200:
            print(response.status_code)
            web_data = response.json()
            break

        if response.status_code in (500, 502, 503, 429, 403):
            print("There was an error with getting a valid response, we'll try again")
            time.sleep(2)
            print(f"Attempt {attempt} has failed retriying")

            if attempt == 3:
                print("All attempts have failed :(")
                break
        else:
            print(f"Failiure code not recognized: {response.status_code}")
            break

    except requests.exceptions.RequestException as e:
        print(f"sorry but the request itself has failed: {e}")

#Looping through the JSON output

domain_set = set()
for certificate in web_data:
    for domain in certificate["dns_names"]:
        domain_set.add(domain)
        if domain.startswith("*."): 
            domain_set.remove(domain)

print(*domain_set, sep="\n") #print domain on every line






