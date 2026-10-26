"""Fail-closed fixture and report contracts for Task-091 W05 qualification."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path, PureWindowsPath
from typing import Any


_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
_FLOAT_FIELDS = ("x1", "y1", "x2", "y2", "conf", "secondary")
_REQUIRED_PHASES = (
    "model_yolo_inference",
    "model_secondary_classifier_inference",
)
_MAX_MANIFEST_BYTES = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _positive_tolerance(value: Any, name: str) -> float:
    number = _finite_number(value, name)
    if number <= 0 or number > 1:
        raise ValueError(f"{name} must be greater than 0 and at most 1")
    return number


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be an integer greater than 0")
    return value


def _normalize_detection(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")

    normalized = {
        field: _finite_number(value.get(field), f"{name}.{field}")
        for field in _FLOAT_FIELDS
    }
    for field in _FLOAT_FIELDS:
        if normalized[field] < 0 or normalized[field] > 1:
            raise ValueError(f"{name}.{field} must be between 0 and 1")
    if normalized["x1"] >= normalized["x2"]:
        raise ValueError(f"{name}.x1 must be less than x2")
    if normalized["y1"] >= normalized["y2"]:
        raise ValueError(f"{name}.y1 must be less than y2")

    class_id = value.get("class")
    if isinstance(class_id, bool) or not isinstance(class_id, int):
        raise ValueError(f"{name}.class must be an integer")
    class_name = value.get("class_name")
    if not isinstance(class_name, str) or not class_name.strip():
        raise ValueError(f"{name}.class_name must be a non-empty string")

    normalized["class"] = class_id
    normalized["class_name"] = class_name
    return normalized


def _detection_sort_key(detection: dict[str, Any]) -> tuple[Any, ...]:
    return (
        detection["class"],
        detection["x1"],
        detection["y1"],
        detection["x2"],
        detection["y2"],
        detection["conf"],
        detection["secondary"],
        detection["class_name"],
    )


def _normalize_detections(values: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ValueError(f"{name} must be an array")
    normalized = [
        _normalize_detection(value, f"{name}[{index}]")
        for index, value in enumerate(values)
    ]
    return sorted(normalized, key=_detection_sort_key)


def _resolve_tile_path(root: Path, value: Any, name: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty relative path")
    relative = Path(value)
    windows_relative = PureWindowsPath(value)
    if relative.is_absolute() or windows_relative.is_absolute():
        raise ValueError(f"{name} must be relative to the manifest")
    if ".." in relative.parts or ".." in windows_relative.parts:
        raise ValueError(f"{name} must not traverse outside the manifest directory")
    resolved = (root / relative).resolve()
    normalized_root = os.path.normcase(str(root))
    normalized_resolved = os.path.normcase(str(resolved))
    if os.path.commonpath((normalized_root, normalized_resolved)) != normalized_root:
        raise ValueError(f"{name} resolves outside the manifest directory")
    if not resolved.is_file():
        raise ValueError(f"{name} does not identify a file")
    return resolved


def load_fixture_manifest(path: str | Path) -> dict[str, Any]:
    """Load and verify a fixed combined-flow fixture manifest."""

    manifest_path = Path(path).resolve(strict=True)
    if manifest_path.stat().st_size > _MAX_MANIFEST_BYTES:
        raise ValueError("fixture manifest exceeds the 1 MiB limit")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("fixture manifest must contain valid JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("fixture manifest must be an object")
    if manifest.get("schema_version") != 1:
        raise ValueError("fixture manifest schema_version must be 1")
    if manifest.get("flow") != "combined-production":
        raise ValueError("fixture manifest flow must be combined-production")

    tolerances = manifest.get("tolerances")
    if not isinstance(tolerances, dict):
        raise ValueError("fixture manifest tolerances must be an object")
    normalized_tolerances = {
        "coordinates": _positive_tolerance(
            tolerances.get("coordinates"),
            "tolerances.coordinates",
        ),
        "confidence": _positive_tolerance(
            tolerances.get("confidence"),
            "tolerances.confidence",
        ),
        "secondary": _positive_tolerance(
            tolerances.get("secondary"),
            "tolerances.secondary",
        ),
    }
    minimum_candidates = _positive_integer(
        manifest.get("minimum_secondary_candidates"),
        "minimum_secondary_candidates",
    )
    minimum_batches = _positive_integer(
        manifest.get("minimum_secondary_batches"),
        "minimum_secondary_batches",
    )

    tiles = manifest.get("tiles")
    if not isinstance(tiles, list) or not tiles:
        raise ValueError("fixture manifest tiles must be a non-empty array")
    root = manifest_path.parent.resolve()
    normalized_tiles = []
    expected_detection_total = 0
    for index, tile in enumerate(tiles):
        if not isinstance(tile, dict):
            raise ValueError(f"tiles[{index}] must be an object")
        resolved_path = _resolve_tile_path(root, tile.get("path"), f"tiles[{index}].path")
        expected_hash = tile.get("sha256")
        if not isinstance(expected_hash, str) or not _SHA256_PATTERN.fullmatch(
            expected_hash
        ):
            raise ValueError(f"tiles[{index}].sha256 must be 64 hexadecimal characters")
        actual_hash = _sha256(resolved_path)
        if actual_hash != expected_hash.lower():
            raise ValueError(f"tiles[{index}] SHA-256 did not match")
        expected_detections = _normalize_detections(
            tile.get("expected_detections"),
            f"tiles[{index}].expected_detections",
        )
        expected_detection_total += len(expected_detections)
        normalized_tiles.append(
            {
                "path": tile["path"],
                "resolved_path": str(resolved_path),
                "sha256": actual_hash,
                "expected_detections": expected_detections,
            }
        )

    if expected_detection_total < minimum_candidates:
        raise ValueError(
            "expected detections must cover minimum_secondary_candidates"
        )

    return {
        "schema_version": 1,
        "flow": "combined-production",
        "tiles": normalized_tiles,
        "tolerances": normalized_tolerances,
        "minimum_secondary_candidates": minimum_candidates,
        "minimum_secondary_batches": minimum_batches,
    }


def _outputs_match(
    expected_tiles: list[dict[str, Any]],
    actual_tiles: list[list[dict[str, Any]]],
    tolerances: dict[str, float],
) -> bool:
    if len(expected_tiles) != len(actual_tiles):
        return False
    tolerance_by_field = {
        "x1": tolerances["coordinates"],
        "y1": tolerances["coordinates"],
        "x2": tolerances["coordinates"],
        "y2": tolerances["coordinates"],
        "conf": tolerances["confidence"],
        "secondary": tolerances["secondary"],
    }
    for tile, actual_detections in zip(expected_tiles, actual_tiles):
        expected_detections = tile["expected_detections"]
        if len(expected_detections) != len(actual_detections):
            return False
        for expected, actual in zip(expected_detections, actual_detections):
            if expected["class"] != actual["class"]:
                return False
            if expected["class_name"] != actual["class_name"]:
                return False
            for field, tolerance in tolerance_by_field.items():
                if abs(expected[field] - actual[field]) > tolerance:
                    return False
    return True


def evaluate_combined_report(
    *,
    manifest: dict[str, Any],
    results: Any,
    performance: Any,
    selected_devices: Any,
    requested_device: str,
) -> dict[str, Any]:
    """Evaluate production combined-flow output against declared fixture facts."""

    detections_valid = True
    normalized_results: list[list[dict[str, Any]]] = []
    try:
        if not isinstance(results, list):
            raise ValueError("results must be an array")
        normalized_results = [
            _normalize_detections(tile, f"results[{index}]")
            for index, tile in enumerate(results)
        ]
    except ValueError:
        detections_valid = False

    if not isinstance(performance, dict):
        performance = {}
    phases = performance.get("phase_timings")
    metadata = performance.get("runtime_metadata")
    if not isinstance(phases, dict):
        phases = {}
    if not isinstance(metadata, dict):
        metadata = {}
    if not isinstance(selected_devices, dict):
        selected_devices = {}

    tile_count_matches = len(normalized_results) == len(manifest["tiles"])
    expected_outputs_match = detections_valid and _outputs_match(
        manifest["tiles"],
        normalized_results,
        manifest["tolerances"],
    )
    candidate_count = metadata.get("secondary_classifier_candidate_count")
    batch_count = metadata.get("secondary_classifier_batches")
    candidates_sufficient = (
        isinstance(candidate_count, int)
        and not isinstance(candidate_count, bool)
        and candidate_count >= manifest["minimum_secondary_candidates"]
    )
    batches_sufficient = (
        isinstance(batch_count, int)
        and not isinstance(batch_count, bool)
        and batch_count >= manifest["minimum_secondary_batches"]
    )
    devices_match = (
        requested_device in ("cpu", "cuda")
        and selected_devices.get("yolo") == requested_device
        and selected_devices.get("efficientnet") == requested_device
        and metadata.get("model_device") == requested_device
        and metadata.get("secondary_classifier_device") == requested_device
    )
    required_phases_recorded = all(
        isinstance(phases.get(name), (int, float))
        and not isinstance(phases.get(name), bool)
        and math.isfinite(float(phases[name]))
        and float(phases[name]) > 0
        for name in _REQUIRED_PHASES
    )
    checks = {
        "tile_count_matches": tile_count_matches,
        "detections_valid": detections_valid,
        "expected_outputs_match": expected_outputs_match,
        "secondary_classifier_enabled": metadata.get(
            "secondary_classifier_enabled"
        )
        is True,
        "secondary_candidates_sufficient": candidates_sufficient,
        "secondary_batches_sufficient": batches_sufficient,
        "devices_match_request": devices_match,
        "required_phases_recorded": required_phases_recorded,
    }
    return {
        "fixture": {
            "flow": manifest["flow"],
            "tiles": [
                {"path": tile["path"], "sha256": tile["sha256"]}
                for tile in manifest["tiles"]
            ],
            "tolerances": dict(manifest["tolerances"]),
        },
        "normalized_results": normalized_results,
        "performance": performance,
        "selected_devices": dict(selected_devices),
        "checks": checks,
        "passed": all(checks.values()),
    }


def verify_fixture_files(manifest: dict[str, Any]) -> None:
    """Reverify every fixed fixture byte before or after model execution."""

    for index, tile in enumerate(manifest["tiles"]):
        path = Path(tile["resolved_path"])
        if not path.is_file() or _sha256(path) != tile["sha256"]:
            raise ValueError(f"tiles[{index}] changed after manifest validation")