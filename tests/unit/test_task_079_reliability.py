import os
import shutil
import sys
import uuid
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock

sys.path.append(os.path.dirname(__file__) + '/../../webapp')

import towerscout
import ts_performance
from towerscout import app
from ts_geocoding import GeocodingProvider, GeocodingResult, RateLimitError
from ts_performance import PerformanceMetrics


def test_reverse_geocode_route_returns_canonical_fallback_for_provider_failure():
    app.config["TESTING"] = True
    client = app.test_client()
    failure_result = GeocodingResult(
        address="",
        provider=GeocodingProvider.AZURE_MAPS,
        confidence=0.0,
        coordinates=(47.6205, -122.3493),
        success=False,
        error_message="provider unavailable",
    )

    with patch.object(towerscout, "azure_api_key", "test-azure-key"), \
         patch.object(towerscout, "google_api_key", ""), \
         patch("ts_geocache.GeocodingCache.get", return_value=None), \
         patch("ts_geocoding.GeocodingService.reverse_geocode", return_value=failure_result):
        response = client.post(
            "/api/geocode/reverse",
            json={"lat": 47.6205, "lng": -122.3493, "provider": "azure"},
        )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["success"] is False
    assert payload["address"] == "Coordinates: 47.620500, -122.349300"
    assert payload["provider"] == "fallback"
    assert payload["error"] == "provider unavailable"


def test_reverse_geocode_route_returns_rate_limited_fallback():
    app.config["TESTING"] = True
    client = app.test_client()

    with patch.object(towerscout, "azure_api_key", "test-azure-key"), \
         patch.object(towerscout, "google_api_key", ""), \
         patch("ts_geocache.GeocodingCache.get", return_value=None), \
         patch(
             "ts_geocoding.GeocodingService.reverse_geocode",
             side_effect=RateLimitError(GeocodingProvider.AZURE_MAPS),
         ):
        response = client.post(
            "/api/geocode/reverse",
            json={"lat": 47.6205, "lng": -122.3493, "provider": "azure"},
        )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["success"] is False
    assert payload["address"] == "Coordinates: 47.620500, -122.349300"
    assert payload["provider"] == "rate_limited"
    assert payload["error_type"] == "RateLimitError"


def test_performance_metrics_accumulates_model_phase_timing_and_metadata():
    metrics = PerformanceMetrics("task-079-test")

    metrics.add_phase_duration("model_yolo_inference", 1.0)
    metrics.add_phase_duration("model_yolo_inference", 2.0)
    metrics.set_runtime_metadata(
        model_device="cpu",
        model_batch_size=4,
        secondary_classifier_enabled=True,
    )

    payload = metrics.to_dict()
    assert payload["phase_timings"]["model_yolo_inference"] == 3.0
    assert payload["runtime_metadata"]["model_device"] == "cpu"
    assert payload["runtime_metadata"]["model_batch_size"] == 4


def test_attach_detection_addresses_skips_outside_boundary_provider_calls():
    app.config["TESTING"] = True
    successful_result = GeocodingResult(
        address="123 Test Street",
        provider=GeocodingProvider.AZURE_MAPS,
        confidence=0.95,
        coordinates=(47.0, -122.0),
        success=True,
    )
    geocoding_service = Mock()
    geocoding_service.reverse_geocode.return_value = successful_result
    geocoding_service.get_session_usage.return_value = Mock(
        google_requests=0,
        azure_requests=1,
        total_requests=1,
        successful_requests=1,
        failed_requests=0,
    )
    geocoding_cache = Mock()
    geocoding_cache.get.return_value = None

    detections = [
        {"class": 0, "inside": True, "x1": -122.1, "x2": -121.9, "y1": 46.9, "y2": 47.1},
        {"class": 0, "inside": False, "x1": -123.1, "x2": -122.9, "y1": 46.9, "y2": 47.1},
        {"class": 1, "inside": True, "x1": -124.1, "x2": -123.9, "y1": 46.9, "y2": 47.1},
    ]

    with app.test_request_context("/"), \
         patch.object(towerscout, "azure_api_key", "test-azure-key"), \
         patch.object(towerscout, "google_api_key", ""), \
         patch.object(towerscout, "create_geocoding_service", return_value=geocoding_service), \
         patch.object(towerscout, "create_geocoding_cache", return_value=geocoding_cache):
        metrics = PerformanceMetrics("geocoding-skip-test")
        towerscout._attach_detection_addresses(detections, "azure", perf_metrics=metrics)

    geocoding_service.reverse_geocode.assert_called_once()
    assert detections[0]["address"] == "123 Test Street"
    assert detections[1]["address"] == "Coordinates: 47.000000, -123.000000"
    assert detections[1]["address_provider"] == "outside_boundary"
    assert detections[2]["address_provider"] == "none"
    assert metrics.runtime_metadata["geocoding_eligible_count"] == 1
    assert metrics.runtime_metadata["geocoding_skipped_outside_boundary_count"] == 1
    assert metrics.runtime_metadata["geocoding_provider_calls"] == 1


def test_performance_estimate_uses_recent_provider_history(monkeypatch):
    scratch_dir = Path(".agent_work/pytest-temp") / f"estimate-history-{uuid.uuid4().hex}"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    try:
        log_path = scratch_dir / "performance.jsonl"
        log_path.write_text(
            "\n".join([
                '{"tile_count": 8, "total_workflow_time_seconds": 16.0, "map_provider": "google"}',
                '{"tile_count": 8, "total_workflow_time_seconds": 64.0, "map_provider": "azure"}',
            ]),
            encoding="utf-8",
        )
        monkeypatch.setattr(ts_performance, "get_log_dir", lambda: scratch_dir)
        monkeypatch.delenv("TOWERSCOUT_ESTIMATE_SECONDS_PER_TILE", raising=False)

        metrics = PerformanceMetrics("estimate-history-test")
        metrics.map_provider = "azure"

        estimate = metrics.estimate_processing_time(8, fixed_overhead_seconds=12.0)

        assert estimate == 76.0
        assert metrics.runtime_metadata["estimate_seconds_per_tile"] == 8.0
        assert metrics.runtime_metadata["estimate_fixed_overhead_seconds"] == 12.0
        assert metrics.runtime_metadata["estimate_history_sample_count"] == 1
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)
