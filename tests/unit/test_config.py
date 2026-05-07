import shutil
import uuid
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

import ts_config
from ts_errors import NetworkError


@pytest.fixture
def temp_config_root():
    base_dir = Path.cwd() / ".agent_work" / "pytest-temp"
    base_dir.mkdir(parents=True, exist_ok=True)
    root = base_dir / f"task046-{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _write_env(root: Path, contents: str) -> Path:
    env_path = root / "config" / ".env"
    env_path.write_text(contents, encoding="utf-8")
    return env_path


@patch("ts_config.requests.get")
def test_validate_api_key_google(mock_get):
    static_response = Mock(status_code=200)
    geocode_response = Mock(status_code=200)
    geocode_response.json.return_value = {
        "status": "OK",
        "results": [{"formatted_address": "123 Test Street"}],
    }
    mock_get.side_effect = [static_response, geocode_response]

    result = ts_config.validate_api_key("google", "google-test-key")

    assert result["valid"] is True
    assert result["provider"] == "google"
    assert "tested_at" in result


@patch("ts_config.requests.get")
def test_validate_api_key_azure(mock_get):
    mock_get.return_value = Mock(status_code=200)

    result = ts_config.validate_api_key("azure", "azure-test-key")

    assert result["valid"] is True
    assert result["provider"] == "azure"
    assert "tested_at" in result


@patch("ts_config.requests.get")
def test_validate_api_key_network_error_returns_network_error(mock_get):
    mock_get.side_effect = requests.RequestException("network down")

    with pytest.raises(NetworkError) as exc_info:
        ts_config.validate_api_key("google", "google-test-key")

    assert exc_info.value.user_message == "Could not reach the provider validation service."


@patch("ts_config.requests.get")
def test_validate_api_key_fails_closed_on_ssl_error_by_default(mock_get, monkeypatch):
    monkeypatch.delenv("TOWERSCOUT_ALLOW_INSECURE_TLS", raising=False)
    mock_get.side_effect = requests.exceptions.SSLError("tls failed")

    with pytest.raises(NetworkError) as exc_info:
        ts_config.validate_api_key("google", "google-test-key")

    assert exc_info.value.user_message == "Could not reach the provider validation service."
    assert mock_get.call_count == 1


@patch("ts_config.requests.get")
def test_validate_api_key_can_bypass_tls_when_explicit_env_set(mock_get, monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_ALLOW_INSECURE_TLS", "1")
    static_response = Mock(status_code=200)
    insecure_success = Mock(status_code=200)
    insecure_success.json.return_value = {"status": "OK", "results": [{"formatted_address": "x"}]}
    mock_get.side_effect = [static_response, insecure_success]

    result = ts_config.validate_api_key("google", "google-test-key")

    assert result["valid"] is True
    assert result["tls_verification_bypassed"] is True
    assert "warning" in result
    assert mock_get.call_args.kwargs["verify"] is False


@patch("ts_config.requests.get")
def test_validate_api_key_azure_falls_back_to_search_probe(mock_get):
    mock_get.side_effect = [
        Mock(status_code=400),
        Mock(status_code=200),
    ]

    result = ts_config.validate_api_key("azure", "azure-test-key")

    assert result["valid"] is True
    assert result["provider"] == "azure"


def test_update_env_file_preserves_existing_comments(temp_config_root, monkeypatch):
    env_path = _write_env(
        temp_config_root,
        "# Existing config\nGOOGLE_API_KEY=old-key\nDEFAULT_MAP_PROVIDER=azure\n"
    )

    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)

    ts_config.update_env_file({
        "GOOGLE_API_KEY": "new-google-key",
        "AZURE_MAPS_SUBSCRIPTION_KEY": "new-azure-key",
        "DEFAULT_MAP_PROVIDER": "google",
    })

    contents = env_path.read_text(encoding="utf-8")
    assert "# Existing config" in contents
    assert "GOOGLE_API_KEY=new-google-key" in contents
    assert "AZURE_MAPS_SUBSCRIPTION_KEY=new-azure-key" in contents
    assert "DEFAULT_MAP_PROVIDER=google" in contents
    backups = list((temp_config_root / "config").glob(".env.backup.*"))
    assert backups


def test_ensure_persistent_flask_secret_key_generates_missing_secret(temp_config_root, monkeypatch):
    _write_env(temp_config_root, "DEFAULT_MAP_PROVIDER=azure\n")
    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)

    secret = ts_config.ensure_persistent_flask_secret_key()

    contents = (temp_config_root / "config" / ".env").read_text(encoding="utf-8")
    assert secret
    assert f"FLASK_SECRET_KEY={secret}" in contents
    assert "GOOGLE_API_KEY" not in contents


def test_ensure_persistent_flask_secret_key_reuses_existing_secret(temp_config_root, monkeypatch):
    _write_env(temp_config_root, "FLASK_SECRET_KEY=existing-secret\n")
    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)

    secret = ts_config.ensure_persistent_flask_secret_key()

    assert secret == "existing-secret"
    assert os.environ["FLASK_SECRET_KEY"] == "existing-secret"


def test_get_env_status_detects_placeholder_values(temp_config_root, monkeypatch):
    _write_env(
        temp_config_root,
        "GOOGLE_API_KEY=your_google_maps_api_key_here\nAZURE_MAPS_SUBSCRIPTION_KEY=\nDEFAULT_MAP_PROVIDER=azure\n"
    )

    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)

    status = ts_config.get_env_status()

    assert status["google"]["configured"] is False
    assert status["azure"]["configured"] is False
    assert status["needs_setup"] is True


def test_get_recent_performance_stats_uses_existing_log(temp_config_root, monkeypatch):
    logs_dir = temp_config_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "performance.log"
    log_path.write_text(
        "timestamp,session_id,tile_count,estimated_time_seconds,actual_model_time_seconds,total_workflow_time_seconds,"
        "detection_count,detections_selected,avg_confidence,memory_usage_mb,gpu_memory_usage_mb,peak_memory_mb,"
        "peak_gpu_memory_mb,map_api_calls,geocoding_api_calls,map_provider,detection_engine,crop_tiles,phase_timings_json\n"
        "2026-03-20T10:00:00,s1,50,10,8,20,4,4,0.8,100,0,100,0,5,1,azure,yolo,false,{}\n"
        "2026-03-20T10:05:00,s2,30,8,7,10,3,3,0.7,100,0,100,0,3,1,google,yolo,false,{}\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)

    stats = ts_config.get_recent_performance_stats()

    assert stats["session_count"] == 2
    assert stats["avg_tiles_per_second"] == pytest.approx(2.75, rel=1e-3)
    assert stats["last_detection_timestamp"] == "2026-03-20T10:05:00"


def test_get_recent_performance_stats_supports_headerless_log_format(temp_config_root, monkeypatch):
    logs_dir = temp_config_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "performance.log"
    log_path.write_text(
        "2026-03-23T13:10:04.909834,2639578019824,10,3.0,43.3,46.25,54,54,0.748,2220.09,0.0,2385.08,0.0,10,9,azure,newest,True,\"{\"\"tile_download\"\": 2.6}\"\n"
        "2026-03-23T14:00:44.877386,2639578019824,4,1.2,9.39,16.27,32,31,0.696,2174.67,0.0,2238.66,0.0,4,13,azure,newest,True,\"{\"\"tile_download\"\": 1.74}\"\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(ts_config, "get_base_dir", lambda: temp_config_root)

    stats = ts_config.get_recent_performance_stats()

    assert stats["session_count"] == 2
    assert stats["avg_tiles_per_second"] == pytest.approx(0.23, rel=1e-2)
    assert stats["last_detection_timestamp"] == "2026-03-23T14:00:44.877386"
