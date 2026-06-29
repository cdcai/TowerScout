import asyncio
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
from flask import session

from towerscout import SESSION_ID_KEY, _get_session_run_id, app
from ts_errors import MapProviderError, NetworkError
from ts_maps import fetch_all


def test_session_run_id_is_persisted_in_session():
    with app.test_request_context("/"):
        session.clear()
        first = _get_session_run_id()
        second = _get_session_run_id()

    assert first == second
    assert first.startswith("session-")


def test_fetch_all_fails_on_partial_download_and_reports_tile_counts():
    fake_fetch = AsyncMock(side_effect=[None, MapProviderError("boom"), None])

    with patch("ts_maps.fetch", fake_fetch):
        try:
            asyncio.run(
                fetch_all(
                    asyncio.Semaphore(1),
                    Mock(),
                    ["tile-0", "tile-1", "tile-2"],
                    "ignored-dir",
                    "ignored-file",
                    False,
                )
            )
            assert False, "Expected a MapProviderError for partial tile download failure"
        except MapProviderError as error:
            assert error.details["successful_tile_count"] == 2
            assert error.details["failed_tile_count"] == 1
            assert error.details["failed_tile_ids"] == [1]


def test_fetch_all_propagates_tls_repair_network_error_with_tile_counts():
    tls_error = NetworkError(
        "TLS certificate validation failed during map tile download",
        details={
            "provider": "google",
            "category": "tls_ca_untrusted",
            "repair_command": ".\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off",
        },
        user_message="Google Maps TLS certificate validation failed.",
    )
    fake_fetch = AsyncMock(side_effect=[None, tls_error, None])

    with patch("ts_maps.fetch", fake_fetch):
        with pytest.raises(NetworkError) as exc_info:
            asyncio.run(
                fetch_all(
                    asyncio.Semaphore(1),
                    Mock(),
                    ["tile-0", "tile-1", "tile-2"],
                    "ignored-dir",
                    "ignored-file",
                    False,
                )
            )

    error = exc_info.value
    assert error.details["category"] == "tls_ca_untrusted"
    assert error.details["repair_command"].startswith(".\\scripts\\repair-provider-tls.cmd")
    assert error.details["successful_tile_count"] == 2
    assert error.details["failed_tile_count"] == 1
    assert error.details["failed_tile_ids"] == [1]


def test_getobjects_reports_imagery_download_failure_before_inference():
    app.config["TESTING"] = True
    client = app.test_client()

    fake_detector = Mock()
    fake_detector.batch_size = 1

    fake_map_provider = Mock()
    fake_map_provider.get_sat_maps.side_effect = MapProviderError(
        "Failed to download required imagery for 1 of 2 tile(s).",
        provider="google",
        details={
            "successful_tile_count": 1,
            "failed_tile_count": 1,
            "failed_tile_ids": [1],
        },
    )

    with patch("towerscout.get_engine", return_value=fake_detector), \
         patch("towerscout._create_map_provider", return_value=fake_map_provider), \
         patch(
             "towerscout._parse_detection_request",
             return_value={
                 "bounds": "37.7,-122.5,37.8,-122.4",
                 "engine": "newest",
                 "provider": "google",
                 "polygons": [],
             },
         ), \
         patch(
             "towerscout._build_tiles_for_request",
             return_value=(
                 [{"id": 0}, {"id": 1}],
                 1,
                 2,
                 10.0,
                 640,
                 640,
                 {
                     "candidate_tiles": 2,
                     "viewport_tiles": 2,
                     "retained_tiles": 2,
                 },
             ),
         ), \
         patch("towerscout._make_session_tmpdir", return_value=tempfile.mkdtemp(prefix="ts-test-")):
        response = client.post("/getobjects", data={"bounds": "x"})

    assert response.status_code == 502
    assert "Imagery download failed" in response.get_json()["error"]
    fake_detector.detect.assert_not_called()

    progress = client.get("/api/detection/progress").get_json()
    assert progress["title"] == "Imagery download failed"
    assert progress["counts"]["imagery_tiles_downloaded"] == 1
    assert progress["counts"]["imagery_tiles_failed"] == 1

    with client.session_transaction() as sess:
        assert sess[SESSION_ID_KEY].startswith("session-")


def test_getobjects_reports_imagery_tls_repair_details_before_inference():
    app.config["TESTING"] = True
    client = app.test_client()

    fake_detector = Mock()
    fake_detector.batch_size = 1

    fake_map_provider = Mock()
    fake_map_provider.get_sat_maps.side_effect = NetworkError(
        "TLS certificate validation failed during map tile download",
        details={
            "provider": "google",
            "category": "tls_ca_untrusted",
            "repair_command": ".\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off",
            "successful_tile_count": 1,
            "failed_tile_count": 1,
            "failed_tile_ids": [1],
        },
        user_message="Google Maps TLS certificate validation failed.",
    )

    with patch("towerscout.get_engine", return_value=fake_detector), \
         patch("towerscout._create_map_provider", return_value=fake_map_provider), \
         patch(
             "towerscout._parse_detection_request",
             return_value={
                 "bounds": "37.7,-122.5,37.8,-122.4",
                 "engine": "newest",
                 "provider": "google",
                 "polygons": [],
             },
         ), \
         patch(
             "towerscout._build_tiles_for_request",
             return_value=(
                 [{"id": 0}, {"id": 1}],
                 1,
                 2,
                 10.0,
                 640,
                 640,
                 {
                     "candidate_tiles": 2,
                     "viewport_tiles": 2,
                     "retained_tiles": 2,
                 },
             ),
         ), \
         patch("towerscout._make_session_tmpdir", return_value=tempfile.mkdtemp(prefix="ts-test-")):
        response = client.post("/getobjects", data={"bounds": "x"})

    payload = response.get_json()
    assert response.status_code == 502
    assert payload["type"] == "NetworkError"
    assert "Imagery download failed" in payload["error"]
    assert "repair-provider-tls.cmd" in payload["error"]
    assert payload["details"]["category"] == "tls_ca_untrusted"
    assert payload["details"]["repair_command"].startswith(".\\scripts\\repair-provider-tls.cmd")
    fake_detector.detect.assert_not_called()

    progress = client.get("/api/detection/progress").get_json()
    assert progress["title"] == "Imagery download failed"
    assert progress["counts"]["imagery_tiles_downloaded"] == 1
    assert progress["counts"]["imagery_tiles_failed"] == 1
