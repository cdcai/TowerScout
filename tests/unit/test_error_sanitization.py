import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

from ts_errors import NetworkError


def test_towerscout_error_dict_sanitizes_cause_and_details():
    cause = RuntimeError(
        "HTTPSConnectionPool url=/maps/api/staticmap?key=AIzaSyDEXAMPLE1234567890abcdefghijklmno"
    )

    error = NetworkError(
        "google validation request failed",
        cause=cause,
        details={
            "url": "https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyDEXAMPLE1234567890abcdefghijklmno"
        },
    )

    payload = error.to_dict()
    serialized = str(payload)

    assert "AIzaSyDEXAMPLE1234567890abcdefghijklmno" not in serialized
    assert "key=***REDACTED***" in serialized
