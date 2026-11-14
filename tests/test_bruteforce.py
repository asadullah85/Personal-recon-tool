import time
from unittest.mock import Mock, patch

import pytest

import concurrency


def _candidate(prefix):
    return f"{prefix}.example.test"


def test_basic_hits_return_only_candidates_with_ips():
    answers = {
        _candidate("www"): ["192.0.2.10"],
        _candidate("api"): ["192.0.2.20"],
    }
    resolver = Mock(side_effect=lambda name: answers.get(name))

    with patch.object(concurrency, "resolve_subdomain", resolver):
        result = concurrency.dns_brute_forcing("example.test", None)

    assert result == answers
    assert all(ips is not None for ips in result.values())


def test_none_wildcard_ips_returns_hits_without_type_error():
    hit = _candidate("www")
    resolver = Mock(side_effect=lambda name: ["192.0.2.10"] if name == hit else None)

    with patch.object(concurrency, "resolve_subdomain", resolver):
        result = concurrency.dns_brute_forcing("example.test", None)

    assert result == {hit: ["192.0.2.10"]}


def test_wildcard_addresses_are_excluded_and_distinct_address_is_kept():
    wildcard_candidate = _candidate("www")
    distinct_candidate = _candidate("api")
    answers = {
        wildcard_candidate: ["203.0.113.1"],
        distinct_candidate: ["198.51.100.2"],
    }
    resolver = Mock(side_effect=lambda name: answers.get(name))

    with patch.object(concurrency, "resolve_subdomain", resolver):
        result = concurrency.dns_brute_forcing("example.test", ["203.0.113.1"])

    assert result == {distinct_candidate: ["198.51.100.2"]}


def test_wildcard_filter_ignores_address_order():
    candidate = _candidate("www")
    resolver = Mock(
        side_effect=lambda name: ["2.2.2.2", "1.1.1.1"] if name == candidate else None
    )

    with patch.object(concurrency, "resolve_subdomain", resolver):
        result = concurrency.dns_brute_forcing(
            "example.test", ["1.1.1.1", "2.2.2.2"]
        )

    assert candidate not in result


def test_threaded_results_match_sequential_results_for_full_prefix_list():
    def answer_for(name):
        last_character = name.split(".", 1)[0][-1]
        if last_character in "02468":
            return ["192.0.2.30"]
        if last_character in "13579":
            return ["198.51.100.40"]
        return None

    threaded_resolver = Mock(side_effect=answer_for)
    with patch.object(concurrency, "resolve_subdomain", threaded_resolver):
        threaded = concurrency.dns_brute_forcing("example.test", None)

    sequential_resolver = Mock(side_effect=answer_for)
    sequential = {}
    for prefix in concurrency.prefixes_list:
        candidate = _candidate(prefix)
        ips = sequential_resolver(candidate)
        if ips is not None:
            sequential[candidate] = ips

    assert threaded == sequential


@pytest.mark.xfail(
    raises=RuntimeError,
    strict=True,
    reason="A worker exception currently propagates from future.result() and crashes the run.",
)
def test_worker_exception_documents_current_crash_behavior():
    failing_candidate = _candidate(concurrency.prefixes_list[0])

    def resolver(name):
        if name == failing_candidate:
            raise RuntimeError("mock resolver failure")
        return ["192.0.2.50"]

    with patch.object(concurrency, "resolve_subdomain", side_effect=resolver):
        result = concurrency.dns_brute_forcing("example.test", None)

    assert failing_candidate not in result


def test_lookups_run_concurrently_with_40_candidates():
    prefixes = [f"host{i}" for i in range(40)]

    def slow_resolver(_name):
        time.sleep(0.1)
        return ["192.0.2.60"]

    with (
        patch.object(concurrency, "prefixes_list", prefixes),
        patch.object(concurrency, "resolve_subdomain", side_effect=slow_resolver),
    ):
        started = time.perf_counter()
        result = concurrency.dns_brute_forcing("example.test", None)
        elapsed = time.perf_counter() - started

    assert len(result) == 40
    assert elapsed < 1.0

