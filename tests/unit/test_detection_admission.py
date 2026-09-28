import io
import shutil
import threading
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image
import pytest

import towerscout
from towerscout import app


def _png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), color="white").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_detection_routes_share_nonblocking_job_admission(monkeypatch):
    app.config["TESTING"] = True
    upload_dir = Path(".agent_work") / "pytest-temp" / f"task091-admission-{uuid.uuid4().hex}"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(towerscout, "UPLOAD_DIR", upload_dir)

    entered_detector = threading.Event()
    release_detector = threading.Event()
    fake_detector = Mock()

    def detect(*_args, **_kwargs):
        entered_detector.set()
        assert release_detector.wait(timeout=5), "test did not release held detector"
        return [[]]

    fake_detector.detect.side_effect = detect
    first_response = {}

    def run_first_request():
        client = app.test_client()
        first_response["response"] = client.post(
            "/getobjectscustom",
            data={
                "engine": "yolo",
                "image": (_png_bytes(), "held-detection.png"),
            },
            content_type="multipart/form-data",
        )

    with towerscout.rate_limiter._lock:
        towerscout.rate_limiter.requests.clear()

    try:
        with patch("towerscout.get_engine", return_value=fake_detector), patch(
            "towerscout._run_detection_request",
            side_effect=lambda: (towerscout.jsonify({"ok": True}), 200),
        ) as run_map_detection:
            worker = threading.Thread(target=run_first_request)
            worker.start()
            assert entered_detector.wait(timeout=5), "first request did not enter detector"

            second_client = app.test_client()
            blocked_response = second_client.post("/getobjects", data={"bounds": "x"})

            assert blocked_response.status_code == 429
            assert blocked_response.get_json()["code"] == "DETECTION_BUSY"
            run_map_detection.assert_not_called()
            assert fake_detector.detect.call_count == 1

            release_detector.set()
            worker.join(timeout=5)
            assert not worker.is_alive()
            assert first_response["response"].status_code == 200

            recovered_response = second_client.post("/getobjects", data={"bounds": "x"})
            assert recovered_response.status_code == 200
            run_map_detection.assert_called_once()
    finally:
        release_detector.set()
        with towerscout.rate_limiter._lock:
            towerscout.rate_limiter.requests.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_detection_admission_releases_after_handler_failure():
    app.config["TESTING"] = True
    client = app.test_client()
    call_count = 0

    def run_detection():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("synthetic detection failure")
        return towerscout.jsonify({"ok": True}), 200

    with patch("towerscout._run_detection_request", side_effect=run_detection):
        with pytest.raises(RuntimeError, match="synthetic detection failure"):
            client.post("/getobjects", data={"bounds": "x"})

        recovered_response = client.post("/getobjects", data={"bounds": "x"})

    assert recovered_response.status_code == 200
    assert recovered_response.get_json() == {"ok": True}
    assert call_count == 2


def test_detection_allocates_cancel_event_before_publishing_progress(monkeypatch):
    app.config["TESTING"] = True
    client = app.test_client()
    order = []
    monkeypatch.setenv("TOWERSCOUT_PILOT_MAX_TILES", "1")

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._parse_detection_request",
        return_value={
            "bounds": "37.7,-122.5,37.8,-122.4",
            "engine": "newest",
            "provider": "azure",
            "polygons": [],
        },
    ), patch(
        "towerscout._register_detection_run",
        side_effect=lambda *_args, **_kwargs: order.append("progress"),
    ), patch.object(
        towerscout.exit_events,
        "alloc",
        side_effect=lambda _run_token: order.append("event"),
    ), patch.object(
        towerscout.exit_events,
        "free",
    ), patch(
        "towerscout._create_map_provider",
        return_value=Mock(),
    ), patch(
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
    ):
        response = client.post("/getobjects", data={"bounds": "x"})

    assert response.status_code == 400
    assert order[:2] == ["event", "progress"]


def test_map_detection_rate_limit_is_checked_before_admission():
    app.config["TESTING"] = True
    client = app.test_client()
    assert towerscout.detection_job_lock.acquire(blocking=False)

    try:
        with patch.object(towerscout.rate_limiter, "is_allowed", return_value=False), patch(
            "towerscout._run_detection_request",
        ) as run_detection:
            response = client.post("/getobjects", data={"bounds": "x"})

        assert response.status_code == 429
        assert response.get_json()["code"] == "RATE_LIMITED"
        run_detection.assert_not_called()
    finally:
        towerscout.detection_job_lock.release()


def test_abort_returns_pending_promptly_while_detection_owns_slot():
    app.config["TESTING"] = True
    detection_entered = threading.Event()
    release_detection = threading.Event()
    cancel_signalled = threading.Event()
    abort_returned = threading.Event()
    responses = {}
    run_token = "session-test:run-token"

    def run_detection():
        detection_entered.set()
        assert release_detection.wait(timeout=5), "test did not release detection"
        return towerscout.jsonify({"ok": True}), 200

    def run_first_request():
        responses["detection"] = app.test_client().post(
            "/getobjects",
            data={"bounds": "x"},
        )

    def run_abort_request():
        responses["abort"] = app.test_client().post("/abort")
        abort_returned.set()

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._run_detection_request",
        side_effect=run_detection,
    ), patch(
        "towerscout._get_session_run_id",
        return_value="session-test",
    ), patch(
        "towerscout._mark_detection_run_cancel_requested",
        return_value={"run_token": run_token},
    ), patch.object(
        towerscout.exit_events,
        "signal",
        side_effect=lambda token: cancel_signalled.set(),
    ) as signal:
        detection_worker = threading.Thread(target=run_first_request)
        abort_worker = threading.Thread(target=run_abort_request)
        detection_worker.start()
        assert detection_entered.wait(timeout=5), "detection did not acquire its slot"

        abort_worker.start()
        assert cancel_signalled.wait(timeout=5), "abort did not signal cancellation"
        assert abort_returned.wait(timeout=1), (
            "abort blocked while detection held the slot"
        )
        assert responses["abort"].status_code == 202
        assert responses["abort"].get_json() == {
            "status": "cancel_requested",
            "retryReady": False,
            "message": (
                "Cancellation is still pending while the current model step "
                "finishes. TowerScout will enable detection when the run stops."
            ),
        }

        release_detection.set()
        detection_worker.join(timeout=5)

        assert not detection_worker.is_alive()
        assert not abort_worker.is_alive()
        signal.assert_called_once_with(run_token)
        assert responses["detection"].status_code == 200

        retry_response = app.test_client().post("/getobjects", data={"bounds": "x"})

    assert retry_response.status_code == 200
    assert retry_response.get_json() == {"ok": True}


def test_abort_without_session_run_is_ready_even_when_global_slot_is_busy():
    app.config["TESTING"] = True
    client = app.test_client()
    assert towerscout.detection_job_lock.acquire(blocking=False)

    try:
        with patch(
            "towerscout._mark_detection_run_cancel_requested",
            return_value=None,
        ), patch.object(towerscout.exit_events, "signal") as signal:
            response = client.post("/abort")

        assert response.status_code == 200
        assert response.get_json() == {
            "status": "idle",
            "retryReady": True,
        }
        signal.assert_not_called()
    finally:
        towerscout.detection_job_lock.release()
