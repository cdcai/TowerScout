"""Run the TASK-052 bounded detection smoke inside a TowerScout container.

This script intentionally mirrors the maintained host-side smoke test while
executing inside the built image against mounted runtime assets.
"""

from __future__ import annotations

import gc
import shutil
import sys
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import torch

import towerscout
from ts_errors import MapProviderError


def _ensure_engine_catalog_loaded() -> None:
    if towerscout.engines:
        return

    if not towerscout.load_model_catalog():
        raise RuntimeError("No YOLO engine metadata is available.")


def main() -> int:
    app = towerscout.app
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "container-smoke-secret"
    client = app.test_client()

    _ensure_engine_catalog_loaded()
    engine_id, engine_meta = next(iter(towerscout.engines.items()))
    model_path = towerscout.YOLO_MODEL_DIR / engine_meta["file"]
    if not model_path.exists():
        raise RuntimeError(f"Model weights are missing at {model_path}.")

    fake_map_provider = Mock()
    fake_map_provider.get_sat_maps.side_effect = MapProviderError(
        "Failed to download required imagery for 1 of 1 tile(s).",
        provider="azure",
        details={
            "successful_tile_count": 0,
            "failed_tile_count": 1,
            "failed_tile_ids": [0],
        },
    )

    original_engine = engine_meta["engine"]
    engine_meta["engine"] = None
    session_tmpdir = (
        towerscout.get_temp_dir()
        / "session"
        / f"task052-container-smoke-{uuid.uuid4().hex}"
    )
    session_tmpdir.mkdir(parents=True, exist_ok=True)

    try:
        with patch("torch.load", new=torch.serialization.load), patch(
            "towerscout._parse_detection_request",
            return_value={
                "bounds": "37.7,-122.5,37.8,-122.4",
                "engine": engine_id,
                "provider": "azure",
                "polygons": [],
                "estimate": None,
            },
        ), patch("towerscout._create_map_provider", return_value=fake_map_provider), patch(
            "towerscout._build_tiles_for_request",
            return_value=(
                [{"id": 0}],
                1,
                1,
                10.0,
                640,
                640,
                {
                    "candidate_tiles": 1,
                    "viewport_tiles": 1,
                    "retained_tiles": 1,
                },
            ),
        ), patch("towerscout._make_session_tmpdir", return_value=str(session_tmpdir)):
            response = client.post("/getobjects", data={"bounds": "ignored"})

        payload = response.get_json()
        if response.status_code != 502:
            raise AssertionError(f"Expected 502 imagery failure, got {response.status_code}: {payload}")
        if "Imagery download failed" not in payload["error"]:
            raise AssertionError(f"Unexpected response payload: {payload}")
        if engine_meta["engine"] is None:
            raise AssertionError("YOLO engine did not load before the imagery failure boundary.")

        progress_payload = client.get("/api/detection/progress").get_json()
        if progress_payload["title"] != "Imagery download failed":
            raise AssertionError(f"Unexpected progress title: {progress_payload}")

        print("container_task052_smoke=pass")
        print(f"engine_id={engine_id}")
        print(f"model_path={model_path}")
        print(f"response_status={response.status_code}")
        print(f"progress_title={progress_payload['title']}")
        return 0
    finally:
        engine_meta["engine"] = original_engine
        shutil.rmtree(session_tmpdir, ignore_errors=True)
        gc.collect()


if __name__ == "__main__":
    sys.exit(main())
