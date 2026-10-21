"""
Integration Test Template - Provider TLS helper POST schema & idempotency

Purpose:
  - Verify the helper HTTP endpoint enforces the allowed POST body shape and
    rejects forbidden runtime/control fields.
  - Exercise idempotency behavior (posting the same authorization twice should
    indicate existing operation or return the expected 202/409 semantics).

Notes:
  - This test targets the external host helper process (the "helper") which
    usually listens on a local port (e.g. 5001). The helper is NOT the Flask
    backend. Run this test only when the helper is intentionally available.

Usage:
  pytest tests/integration/test_provider_tls_server_side_template.py

Environment:
  Set `TEST_HELPER_BASE_URL` to the helper base URL (default: http://localhost:5001)

"""
import os
import time
import requests
import pytest
import secrets


HELPER_BASE = os.getenv('TEST_HELPER_BASE_URL', 'http://localhost:5001')
POST_PATH = '/operations/provider-tls-repair'


def helper_available():
    try:
        r = requests.get(HELPER_BASE, timeout=1)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not helper_available(), reason="Host helper not reachable on TEST_HELPER_BASE_URL")
def test_helper_accepts_allowed_fields_and_rejects_forbidden():
    url = HELPER_BASE.rstrip('/') + POST_PATH

    # Allowed minimal body
    allowed = {
        'provider': 'google',
        'confirmation': 'repair_tls_and_restart',
        'operation_authorization': 'TEST_OP_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    }

    resp = requests.post(url, json=allowed, timeout=5)
    # TODO: adapt assertions to your helper's expected status code for 'planned'
    assert resp.status_code in (200, 202, 201), f"Expected success/planned, got {resp.status_code} {resp.text}"

    # Forbidden fields should be rejected by the helper (defense-in-depth)
    forbidden = allowed.copy()
    forbidden['engine'] = 'docker'
    forbidden['script_path'] = 'scripts/evil.cmd'

    resp2 = requests.post(url, json=forbidden, timeout=5)
    assert resp2.status_code in (400, 422, 409), (
        f"Expected helper to reject unexpected runtime/control fields, got {resp2.status_code} {resp2.text}"
    )


@pytest.mark.skipif(not helper_available(), reason="Host helper not reachable on TEST_HELPER_BASE_URL")
def test_helper_idempotent_start_and_existing_operation():
    url = HELPER_BASE.rstrip('/') + POST_PATH

    # Make a long, random token to satisfy helper token pattern expectations
    token = f"TEST_OP_TOKEN_{secrets.token_hex(16)}"
    payload = {
        'provider': 'google',
        'confirmation': 'repair_tls_and_restart',
        'operation_authorization': token
    }

    first = requests.post(url, json=payload, timeout=5)
    assert first.status_code in (200, 201, 202), f"Initial start failed: {first.status_code} {first.text}"

    # Re-post same payload; helper should indicate existing operation or return 409
    second = requests.post(url, json=payload, timeout=5)
    assert second.status_code in (200, 202, 409), (
        f"Expected existing-operation semantics on duplicate start, got {second.status_code} {second.text}"
    )
