"""Shared TLS configuration helpers for provider HTTP requests."""

from __future__ import annotations

import os
from pathlib import Path

from ts_errors import NetworkError

INSECURE_TLS_ENV_VAR = "TOWERSCOUT_ALLOW_INSECURE_TLS"
TLS_CA_BUNDLE_ENV_VARS = ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE")
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}


def allow_insecure_tls() -> bool:
    """Return True only when support explicitly disables TLS verification."""
    return os.getenv(INSECURE_TLS_ENV_VAR, "").strip().lower() in TRUTHY_ENV_VALUES


def configured_tls_bundle_error() -> NetworkError | None:
    """Return an actionable error if a configured CA bundle path is unusable."""
    for env_var in TLS_CA_BUNDLE_ENV_VARS:
        configured_path = os.getenv(env_var, "").strip()
        if not configured_path:
            continue

        bundle_path = Path(configured_path)
        if not bundle_path.is_file():
            return NetworkError(
                f"Configured TLS CA bundle path does not exist: {env_var}={configured_path}",
                user_message=(
                    "The configured TLS CA bundle was not found. "
                    "Run scripts/import-tls-ca.cmd for the selected Docker or Podman engine, "
                    "or update REQUESTS_CA_BUNDLE and SSL_CERT_FILE to a valid certificate bundle."
                ),
                details={
                    "env_var": env_var,
                    "configured_path": configured_path,
                    "category": "tls_ca_bundle",
                    "support_action": "Run scripts/import-tls-ca.cmd for the selected container engine.",
                },
            )

    return None


def validate_configured_tls_bundle() -> None:
    """Raise before provider requests when the configured CA bundle is invalid."""
    bundle_error = configured_tls_bundle_error()
    if bundle_error is not None:
        raise bundle_error


def tls_verification_enabled() -> bool:
    """Return whether provider requests should verify TLS certificates."""
    return not allow_insecure_tls()
