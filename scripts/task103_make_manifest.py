"""Build the Task-091 combined-flow fixture manifest from a TASK-103 reference capture.

The reference is the stage-A (accepted main) CPU ``combined`` capture. Tolerances
and minimum EfficientNet work come from the pre-declared gates file, never from
the capture. Tiles are copied next to the manifest because the Task-091 contract
requires tile paths relative to the manifest directory.

Usage:
  python scripts/task103_make_manifest.py --gates scripts/task103_gates.v1.json \
      --capture <run_dir>/combined.json --tiles <fixture source dir> --out <new dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(gates: dict[str, Any], capture: dict[str, Any], capture_sha256: str) -> dict[str, Any]:
    if capture.get("phase") != "combined" or capture.get("mode") != "capture":
        raise ValueError("capture must be a combined phase report in capture mode")
    if not capture.get("ok"):
        raise ValueError("capture report is not ok; refusing to build a reference from it")
    if not capture.get("tile_hashes_verified"):
        raise ValueError("capture did not verify fixture bytes before and after inference")

    declared = [(tile["name"], tile["sha256"].lower()) for tile in gates["fixture"]["tiles"]]
    captured = [(tile["name"], tile["sha256"].lower()) for tile in capture["tiles"]]
    if declared != captured:
        raise ValueError("captured tile names/hashes differ from the gates file")

    measured = [run for run in capture["runs"] if not run["warmup"]]
    if not measured:
        raise ValueError("capture has no measured runs")
    reference = measured[-1]
    if any(run["en"]["errors"] for run in capture["runs"]):
        raise ValueError("capture recorded EfficientNet errors")
    if reference["en"]["candidates"] < 1 or reference["en"]["batches"] < 1:
        raise ValueError("capture did not exercise EfficientNet")

    tolerances = gates["tolerances"]
    return {
        "schema_version": 1,
        "flow": "combined-production",
        "tolerances": {
            "coordinates": tolerances["box"],
            "confidence": tolerances["conf"],
            "secondary": tolerances["secondary"],
        },
        "minimum_secondary_candidates": reference["en"]["candidates"],
        "minimum_secondary_batches": reference["en"]["batches"],
        "tiles": [
            {"path": name, "sha256": digest, "expected_detections": detections}
            for (name, digest), detections in zip(declared, reference["results"])
        ],
        "provenance": {
            "reference_stage": capture.get("stage"),
            "reference_profile": capture.get("profile"),
            "reference_run_id": capture.get("run_id"),
            "reference_capture_sha256": capture_sha256,
            "reference_run_index": reference["index"],
            "per_tile_counts": [len(detections) for detections in reference["results"]],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gates", required=True, type=Path)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--tiles", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    manifest = build_manifest(gates, capture, _sha256(args.capture))

    if args.out.exists():
        print(f"Refusing to overwrite existing directory: {args.out}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True)
    for tile in manifest["tiles"]:
        source = args.tiles / tile["path"]
        if _sha256(source) != tile["sha256"]:
            print(f"Source tile hash mismatch: {source}", file=sys.stderr)
            return 1
        shutil.copy2(source, args.out / tile["path"])
    manifest_path = args.out / "fixture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {manifest_path} ({sum(manifest['provenance']['per_tile_counts'])} expected detections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
