#!/usr/bin/env python3
"""Summarize a TowerScout release directory or zip file."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

INTERESTING = (
    "compose.yaml",
    "Dockerfile",
    ".env.example",
    "README",
    "QUICKSTART",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES",
    "MODEL_LICENSES",
    "DATA_LICENSES",
    "PROVIDER_TERMS",
    "SOURCE",
    "SBOM",
    "release-manifest",
    "checksums",
    "asset_manifest",
)


def from_zip(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(info.filename for info in zf.infolist() if not info.is_dir())


def from_dir(path: Path) -> list[str]:
    return sorted(str(p.relative_to(path)).replace("\\", "/") for p in path.rglob("*") if p.is_file())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_release_package.py RELEASE_DIR_OR_ZIP", file=sys.stderr)
        return 2

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"ERROR: not found: {target}")
        return 1

    names = from_zip(target) if target.suffix.lower() == ".zip" else from_dir(target)
    print(f"target: {target}")
    print(f"file count: {len(names)}")
    print("interesting files:")
    found = False
    for name in names:
        upper = Path(name).name.upper()
        if any(token.upper() in upper for token in INTERESTING):
            print(f"  {name}")
            found = True
    if not found:
        print("  (none matched the default interesting-file list)")

    print("top-level entries:")
    for item in sorted({name.split('/')[0] for name in names})[:200]:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
