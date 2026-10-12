import requests #this is core.py I
import time
import dns.resolver

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
