#!/usr/bin/env python3
"""Scan likely TowerScout license/release claim files for key terms."""
from __future__ import annotations

from pathlib import Path

TERMS = [
    "MIT",
    "Apache",
    "AGPL",
    "GPL",
    "CC-BY",
    "CC BY",
    "YOLO",
    "Ultralytics",
    "commercial",
    "non-commercial",
    "open source",
    "public release",
]

CANDIDATES = [
    "README.md",
    "package.json",
    "LICENSE",
    "LICENSE.TXT",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "MODEL_LICENSES.md",
    "DATA_LICENSES.md",
    "PROVIDER_TERMS.md",
    "SOURCE.txt",
    "SBOM.txt",
    "release-manifest.v1.json",
    "docs/release-asset-bundle-contract.md",
]


def main() -> int:
    root = Path.cwd()
    found = False
    for rel in CANDIDATES:
        path = root / rel
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            low = line.lower()
            hits = [term for term in TERMS if term.lower() in low]
            if hits:
                found = True
                snippet = line.strip()[:240]
                print(f"{rel}:{lineno}: {', '.join(hits)}: {snippet}")
    if not found:
        print("No configured license/release terms found in candidate files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
