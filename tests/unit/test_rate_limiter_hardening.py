from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from ts_validation import RateLimiter


def test_rate_limiter_rejects_invalid_capacity():
    try:
        RateLimiter(max_keys=0)
    except ValueError as error:
        assert "max_keys" in str(error)
    else:
        raise AssertionError("RateLimiter accepted an invalid capacity")


def test_rate_limiter_evicts_oldest_key_and_stays_bounded():
    limiter = RateLimiter(max_keys=2)
    with patch("ts_validation.time.time", side_effect=[10.0, 20.0, 30.0]):
        assert limiter.is_allowed("oldest")
        assert limiter.is_allowed("newer")
        assert limiter.is_allowed("newest")

    assert set(limiter.requests) == {"newer", "newest"}
    assert len(limiter.requests) == limiter.max_keys


def test_rate_limiter_serializes_concurrent_updates():
    limiter = RateLimiter(max_keys=4)
    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(
            executor.map(
                lambda _index: limiter.is_allowed(
                    "same-client",
                    max_requests=10,
                    window_seconds=60,
                ),
                range(30),
            )
        )

    assert results.count(True) == 10
    assert results.count(False) == 20
    assert len(limiter.requests["same-client"]) == 10
