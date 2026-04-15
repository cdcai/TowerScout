from ts_progress import DetectionProgressTracker


def test_progress_tracker_lifecycle_and_counts():
    tracker = DetectionProgressTracker()
    session_id = "session-1"
    run_token = "run-1"

    started = tracker.start(
        session_id,
        run_token,
        provider="azure",
        engine="yolo",
        tile_count=0,
        phase="preparing_tiles",
        title="Preparing tiles",
        detail="Starting detection request...",
    )

    assert started["status"] == "running"
    assert started["phase"] == "preparing_tiles"
    assert started["provider"] == "azure"
    assert started["run_token"] == run_token

    updated = tracker.update(
        session_id,
        run_token=run_token,
        phase="running_model",
        title="Running model detection",
        detail="Processed 8/16 tiles across 1/2 model batches.",
        counts={"model_batches_completed": 1, "model_batches_total": 2},
        tile_count=16,
    )

    assert updated["phase"] == "running_model"
    assert updated["tile_count"] == 16
    assert updated["counts"]["model_batches_completed"] == 1
    assert updated["counts"]["model_batches_total"] == 2

    finished = tracker.finish(
        session_id,
        "completed",
        run_token=run_token,
        phase="complete",
        title="Detection complete",
        detail="Returned 5 detections across 16 tiles.",
        counts={"retained_detections": 5},
        cancel_requested=False,
    )

    assert finished["status"] == "completed"
    assert finished["phase"] == "complete"
    assert finished["counts"]["retained_detections"] == 5

    public_state = tracker.get(session_id)
    assert public_state["status"] == "completed"
    assert "run_token" not in public_state


def test_progress_tracker_rejects_stale_run_tokens_and_can_clear():
    tracker = DetectionProgressTracker()
    session_id = "session-2"

    tracker.start(session_id, "run-active", provider="google", engine="yolo")

    stale_update = tracker.update(
        session_id,
        run_token="run-stale",
        phase="error",
        title="Should not apply",
    )
    assert stale_update is None
    assert tracker.get(session_id)["phase"] == "preparing_tiles"

    cancel_state = tracker.mark_cancel_requested(session_id)
    assert cancel_state["status"] == "cancel_requested"
    assert cancel_state["cancel_requested"] is True

    cleared = tracker.clear(session_id, run_token="run-active")
    assert cleared is True
    assert tracker.get(session_id)["status"] == "idle"
