#!/usr/bin/env python3
"""Check TowerScout frontend source/bundle consistency heuristics."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
SRC = ROOT / "webapp" / "js" / "src"
BUNDLE = ROOT / "webapp" / "js" / "towerscout.js"
BUILD = ROOT / "webapp" / "build.js"


def git_changed() -> set[str]:
    try:
        out = subprocess.check_output(["git", "-C", str(ROOT), "status", "--short"], text=True)
    except Exception:
        return set()
    paths = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SRC.exists():
        errors.append("missing webapp/js/src")
    if not BUNDLE.exists():
        errors.append("missing webapp/js/towerscout.js")
    if not BUILD.exists():
        errors.append("missing webapp/build.js")

    changed = git_changed()
    src_changed = any(p.startswith("webapp/js/src/") for p in changed)
    bundle_changed = "webapp/js/towerscout.js" in changed
    build_changed = "webapp/build.js" in changed

    if src_changed and not bundle_changed:
        warnings.append("source changed but generated bundle is not changed; run node webapp/build.js or explain why")
    if bundle_changed and not src_changed and not build_changed:
        warnings.append("generated bundle changed without source/build changes; verify it was not edited by hand")
    if build_changed:
        warnings.append("build script changed; inspect MODULE_ORDER and run browser/provider validation if load order changed")

    print("TowerScout frontend bundle consistency check")
    print(f"root: {ROOT}")
    print(f"source dir exists: {SRC.exists()}")
    print(f"bundle exists: {BUNDLE.exists()}")
    print(f"build script exists: {BUILD.exists()}")
    print(f"source changed: {src_changed}")
    print(f"bundle changed: {bundle_changed}")
    print(f"build changed: {build_changed}")

    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
