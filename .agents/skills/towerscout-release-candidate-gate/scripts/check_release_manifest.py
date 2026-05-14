#!/usr/bin/env python3
"""Basic TowerScout release manifest checker.

Usage:
  python check_release_manifest.py path/to/release-manifest.v1.json [release-root]

The script intentionally checks only generic structure and referenced file presence.
It does not decide legal adequacy or release approval.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RECOMMENDED_KEYS = {
    "releaseVersion",
    "releasePosture",
    "sourceRef",
    "image",
    "checksums",
}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_release_manifest.py MANIFEST [RELEASE_ROOT]", file=sys.stderr)
        return 2

    manifest_path = Path(sys.argv[1])
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else manifest_path.parent

    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}")
        return 1

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: failed to parse JSON: {exc}")
        return 1

    if not isinstance(data, dict):
        print("ERROR: manifest root must be an object")
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(RECOMMENDED_KEYS - set(data))
    for key in missing:
        warnings.append(f"recommended key missing: {key}")

    image = data.get("image")
    if isinstance(image, dict):
        digest = image.get("digest") or image.get("pinnedDigest") or image.get("imageDigest")
        if not digest or "sha256:" not in str(digest):
            warnings.append("image digest is missing or does not look pinned to sha256")
    elif image is not None:
        if "@sha256:" not in str(image) and "sha256:" not in str(image):
            warnings.append("image field does not look digest-pinned")

    checksums = data.get("checksums")
    if isinstance(checksums, dict):
        for rel_path in checksums:
            candidate = root / str(rel_path)
            if not candidate.exists():
                warnings.append(f"checksum references missing file: {rel_path}")
    elif checksums is not None:
        warnings.append("checksums should be an object mapping files to hashes")

    print(f"manifest: {manifest_path}")
    print(f"release root: {root}")
    print(f"keys: {', '.join(sorted(data.keys()))}")

    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
