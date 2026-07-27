import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

from ts_errors import NetworkError
from ts_logging import sanitize_sensitive_data


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


def test_model_upload_key_is_sanitized_in_logs_and_structured_errors():
    model_upload_key = "model-upload-key-that-must-never-be-logged"
    sensitive_message = (
        f"X-TowerScout-Model-Upload-Key: {model_upload_key} "
        f"TOWERSCOUT_MODEL_UPLOAD_KEY={model_upload_key}"
    )

    sanitized_log = sanitize_sensitive_data(sensitive_message)
    payload = NetworkError(
        sensitive_message,
        details={"request_header": sensitive_message},
    ).to_dict()

    assert model_upload_key not in sanitized_log
    assert model_upload_key not in str(payload)
    assert sanitized_log.count("***REDACTED***") == 2
