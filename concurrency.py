from concurrent.futures import ThreadPoolExecutor, as_completed
from core import resolve_subdomain
from prefix import prefixes_list


def dns_brute_forcing(base_domain, wildcard_ips):
    candidates = [f"{prefix}.{base_domain}" for prefix in prefixes_list]

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_candidate = {}
        result = {}

        for candidate in candidates:
            future = executor.submit(resolve_subdomain, candidate)
            future_to_candidate[future] = candidate

        for future in as_completed(future_to_candidate):
            candidate = future_to_candidate[future]
            try:
                ips = future.result()
            except Exception as e:
                print(f"{candidate}: lookup failed ({type(e).__name__}: {e})")
                continue

            if ips is None:
                continue

            if wildcard_ips and any(ip in wildcard_ips for ip in ips):
                continue

            result[candidate] = ips

    return result
<<<<<<< HEAD
=======





>>>>>>> 1d6e034 (Add scan history and improve subdomain enumeration)
