"""Shared provider HTTP, TLS, and redaction helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import ssl
from typing import Any, Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from ts_errors import NetworkError
from ts_tls import TLS_CA_BUNDLE_ENV_VARS, allow_insecure_tls


TLS_OK = "tls_ok"
TLS_CA_UNTRUSTED = "tls_ca_untrusted"
TLS_BUNDLE_MISSING = "tls_bundle_missing"
TLS_BUNDLE_UNUSABLE = "tls_bundle_unusable"
PROVIDER_TIMEOUT = "provider_timeout"
PROVIDER_NETWORK_BLOCKED = "provider_network_blocked"
PROVIDER_HTTP_ERROR = "provider_http_error"
INVALID_PROVIDER_KEY = "invalid_provider_key"
PROVIDER_API_NOT_AUTHORIZED = "provider_api_not_authorized"

TLS_REPAIR_CATEGORIES = frozenset(
    {
        TLS_CA_UNTRUSTED,
        TLS_BUNDLE_MISSING,
        TLS_BUNDLE_UNUSABLE,
    }
)
TLS_REPAIR_ENGINES = frozenset({"auto", "docker", "podman"})
TLS_REPAIR_GPU_MODES = frozenset({"off", "auto", "on"})

SENSITIVE_QUERY_KEYS = frozenset(
    {
        "key",
        "subscription-key",
        "client_secret",
        "token",
        "access_token",
        "api_key",
        "apikey",
    }
)


@dataclass(frozen=True)
class ProviderTlsConfig:
    """TLS verification settings resolved for one provider request."""

    verify: bool | str
    bundle_path: str | None
    tls_verification_bypassed: bool


def provider_display_name(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "google":
        return "Google Maps"
    if normalized == "azure":
        return "Azure Maps"
    return provider or "provider"


def provider_hostname(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "google":
        return "maps.googleapis.com"
    if normalized == "azure":
        return "atlas.microsoft.com"
    return normalized


def _normalize_repair_option(value: str | None, allowed: frozenset[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


def provider_repair_command(provider: str, engine: str | None = None, gpu: str | None = None) -> str:
    resolved_engine = _normalize_repair_option(
        engine if engine is not None else os.getenv("TOWERSCOUT_CONTAINER_ENGINE"),
        TLS_REPAIR_ENGINES,
        "auto",
    )
    resolved_gpu = _normalize_repair_option(
        gpu if gpu is not None else os.getenv("TOWERSCOUT_GPU_MODE"),
        TLS_REPAIR_GPU_MODES,
        "off",
    )
    return (
        f".\\scripts\\repair-provider-tls.cmd -Provider {provider} "
        f"-Engine {resolved_engine} -Gpu {resolved_gpu}"
    )


def provider_support_action(category: str | None, provider: str) -> str | None:
    if category in TLS_REPAIR_CATEGORIES:
        return (
            f"Import the trusted organization/root TLS CA into the container trust store, "
            f"then retry {provider_display_name(provider)}. Suggested command: "
            f"{provider_repair_command(provider)}"
        )
    if category == PROVIDER_TIMEOUT:
        return "Check network/VPN/proxy connectivity to the provider endpoint and retry."
    if category == PROVIDER_NETWORK_BLOCKED:
        return "Check firewall/proxy/VPN rules for outbound HTTPS access to the provider endpoint."
    return None


def provider_repairable(category: str | None) -> bool:
    return category in TLS_REPAIR_CATEGORIES


def provider_helper_available(_provider: str, _category: str | None) -> bool:
    return False


def provider_user_message(category: str | None, provider: str) -> str:
    label = provider_display_name(provider)
    if category == TLS_CA_UNTRUSTED:
        return (
            f"TowerScout could not verify the {label} TLS certificate. "
            "If this is a managed network, run the provider TLS repair command from the release package."
        )
    if category == TLS_BUNDLE_MISSING:
        return (
            "The configured TLS CA bundle was not found. "
            "Run the provider TLS repair command or update REQUESTS_CA_BUNDLE/SSL_CERT_FILE to a valid bundle."
        )
    if category == TLS_BUNDLE_UNUSABLE:
        return (
            "The configured TLS CA bundle could not be used. "
            "Run the provider TLS repair command or update REQUESTS_CA_BUNDLE/SSL_CERT_FILE to a valid bundle."
        )
    if category == PROVIDER_TIMEOUT:
        return f"TowerScout timed out while reaching {label}. Check internet, VPN, or proxy access, then retry."
    if category == PROVIDER_NETWORK_BLOCKED:
        return (
            f"TowerScout could not reach {label} from the local runtime. "
            "Check internet, firewall, VPN, or proxy access, then retry."
        )
    return f"{label} request failed."


def redact_provider_url(url: str | None, params: Mapping[str, Any] | None = None) -> str | None:
    """Return a provider URL with sensitive query values redacted."""

    if not url:
        return url

    split = urlsplit(str(url))
    query_items = parse_qsl(split.query, keep_blank_values=True)
    if params:
        query_items.extend((str(key), "" if value is None else str(value)) for key, value in params.items())

    redacted_items = []
    for key, value in query_items:
        if key.lower() in SENSITIVE_QUERY_KEYS:
            redacted_items.append((key, "[REDACTED]"))
        else:
            redacted_items.append((key, value))

    redacted_query = urlencode(redacted_items, doseq=True)
    return urlunsplit((split.scheme, split.netloc, split.path, redacted_query, split.fragment))


def _configured_bundle_path() -> str | None:
    for env_var in TLS_CA_BUNDLE_ENV_VARS:
        raw_value = os.environ.get(env_var)
        if raw_value:
            return raw_value
    return None


def _network_error(
    *,
    provider: str,
    category: str,
    message: str,
    cause: Exception | None = None,
    timeout: float | None = None,
    details: dict[str, Any] | None = None,
    url: str | None = None,
) -> NetworkError:
    merged_details: dict[str, Any] = {
        "provider": provider,
        "category": category,
        "repairable": provider_repairable(category),
        "helper_available": provider_helper_available(provider, category),
        "provider_host": provider_hostname(provider),
        "method": "GET",
    }
    if timeout is not None:
        merged_details["timeout_seconds"] = timeout
    if details:
        merged_details.update(details)

    support_action = provider_support_action(category, provider)
    if support_action:
        merged_details["support_action"] = support_action
        if category in TLS_REPAIR_CATEGORIES:
            merged_details["repair_command"] = provider_repair_command(provider)

    return NetworkError(
        message,
        url=url,
        cause=cause,
        timeout=timeout,
        user_message=provider_user_message(category, provider),
        details=merged_details,
    )


def resolve_provider_tls_config(provider: str) -> ProviderTlsConfig:
    if allow_insecure_tls():
        return ProviderTlsConfig(verify=False, bundle_path=None, tls_verification_bypassed=True)

    bundle_path = _configured_bundle_path()
    if not bundle_path:
        return ProviderTlsConfig(verify=True, bundle_path=None, tls_verification_bypassed=False)

    path = Path(bundle_path)
    if not path.is_file():
        raise _network_error(
            provider=provider,
            category=TLS_BUNDLE_MISSING,
            message=f"Configured TLS CA bundle was not found for {provider_display_name(provider)}.",
            details={"bundle_path": bundle_path},
        )

    return ProviderTlsConfig(
        verify=str(path),
        bundle_path=str(path),
        tls_verification_bypassed=False,
    )


def create_provider_ssl_context(provider: str) -> ssl.SSLContext | bool:
    tls_config = resolve_provider_tls_config(provider)
    if tls_config.tls_verification_bypassed:
        return False
    try:
        if tls_config.bundle_path:
            return ssl.create_default_context(cafile=tls_config.bundle_path)
        return ssl.create_default_context()
    except OSError as exc:
        raise _network_error(
            provider=provider,
            category=TLS_BUNDLE_UNUSABLE,
            message=f"Configured TLS CA bundle could not be loaded for {provider_display_name(provider)}.",
            cause=exc,
            details={"bundle_path": tls_config.bundle_path},
        ) from exc


def provider_get(
    provider: str,
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    timeout: float = 10,
    purpose: str = "provider request",
    **kwargs: Any,
) -> requests.Response:
    """Run a provider GET with consistent TLS handling and sanitized failures."""

    redacted_url = redact_provider_url(url, params)
    try:
        tls_config = resolve_provider_tls_config(provider)
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            verify=tls_config.verify,
            **kwargs,
        )
        setattr(response, "_towerscout_provider", provider)
        setattr(response, "_towerscout_redacted_url", redacted_url)
        setattr(response, "_towerscout_tls_verification_bypassed", tls_config.tls_verification_bypassed)
        setattr(response, "_towerscout_tls_bundle_path", tls_config.bundle_path)
        return response
    except requests.Timeout as exc:
        raise _network_error(
            provider=provider,
            category=PROVIDER_TIMEOUT,
            message=f"Timed out during {purpose} for {provider_display_name(provider)}.",
            cause=exc,
            timeout=timeout,
            url=redacted_url,
        ) from exc
    except requests.exceptions.SSLError as exc:
        raise _network_error(
            provider=provider,
            category=TLS_CA_UNTRUSTED,
            message=(
                f"TLS certificate validation failed for {provider_display_name(provider)}. "
                "The container may not trust the organization/root CA."
            ),
            cause=exc,
            timeout=timeout,
            url=redacted_url,
        ) from exc
    except requests.RequestException as exc:
        raise _network_error(
            provider=provider,
            category=PROVIDER_NETWORK_BLOCKED,
            message=f"Network request failed during {purpose} for {provider_display_name(provider)}.",
            cause=exc,
            timeout=timeout,
            url=redacted_url,
        ) from exc
    except OSError as exc:
        raise _network_error(
            provider=provider,
            category=TLS_BUNDLE_UNUSABLE,
            message=f"TLS CA bundle could not be used for {provider_display_name(provider)}.",
            cause=exc,
            timeout=timeout,
            url=redacted_url,
        ) from exc


def response_redacted_url(response: requests.Response) -> str | None:
    return getattr(response, "_towerscout_redacted_url", None) or redact_provider_url(getattr(response, "url", None))


def response_tls_verification_bypassed(response: requests.Response) -> bool:
    return bool(getattr(response, "_towerscout_tls_verification_bypassed", False))


def classify_provider_response(
    provider: str,
    response: requests.Response,
    *,
    body_json: Mapping[str, Any] | None = None,
    auth_failure_is_tls_ok: bool = False,
) -> str:
    status_code = getattr(response, "status_code", None)
    if status_code and 200 <= int(status_code) < 300:
        if provider == "google":
            if not body_json or not isinstance(body_json, Mapping):
                return PROVIDER_HTTP_ERROR
            google_status = str(body_json.get("status", "")).upper()
            if google_status == "OK" or google_status == "ZERO_RESULTS":
                return TLS_OK
            if google_status == "REQUEST_DENIED":
                error_message = str(body_json.get("error_message", "")).lower()
                if auth_failure_is_tls_ok:
                    return TLS_OK
                if "billing" in error_message or "not authorized" in error_message or "not activated" in error_message:
                    return PROVIDER_API_NOT_AUTHORIZED
                return INVALID_PROVIDER_KEY
            if google_status in {"INVALID_REQUEST", "OVER_QUERY_LIMIT"}:
                return PROVIDER_HTTP_ERROR
        return TLS_OK

    if auth_failure_is_tls_ok and status_code in {400, 401, 403}:
        return TLS_OK
    if status_code in {401, 403}:
        return INVALID_PROVIDER_KEY
    return PROVIDER_HTTP_ERROR


def provider_response_summary(response: requests.Response) -> dict[str, Any]:
    return {
        "status_code": getattr(response, "status_code", None),
        "url": response_redacted_url(response),
        "tls_verification_bypassed": response_tls_verification_bypassed(response),
    }
