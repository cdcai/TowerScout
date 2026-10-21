#!/usr/bin/env python3
"""Lightweight end-user docs command/path checker.

Usage:
  python check_doc_commands.py REPO_ROOT [DOC_PATH ...]

The script scans Markdown docs for common command/path references that may need manual verification.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

COMMAND_HINTS = ["start.bat", "launch.ps1", "status.cmd", "logs.cmd", "compose", "podman", "docker", "curl", "api/readiness"]
PATH_HINTS = ["compose.yaml", ".env.example", "asset_manifest.v1.json", "model_params", "data", "logs", "config"]


def iter_docs(root: Path, targets: list[str]):
    if targets:
        for item in targets:
            path = (root / item).resolve() if not Path(item).is_absolute() else Path(item)
            if path.is_dir():
                yield from path.rglob("*.md")
            elif path.exists() and path.suffix.lower() in {".md", ".txt"}:
                yield path
    else:
        for base in [root / "README.md", root / "docs"]:
            if base.is_dir():
                yield from base.rglob("*.md")
            elif base.exists():
                yield base


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_doc_commands.py REPO_ROOT [DOC_PATH ...]", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    targets = sys.argv[2:]
    docs = sorted(set(iter_docs(root, targets)))
    print(f"repo root: {root}")
    print(f"docs scanned: {len(docs)}")
    for doc in docs:
        rel = doc.relative_to(root) if str(doc).startswith(str(root)) else doc
        text = doc.read_text(encoding="utf-8", errors="replace")
        hits = sorted({hint for hint in COMMAND_HINTS + PATH_HINTS if hint.lower() in text.lower()})
        if hits:
            print(f"{rel}: references {', '.join(hits)}")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "http://127.0.0.1" in line:
                print(f"WARN {rel}:{lineno}: docs mention 127.0.0.1; release browser docs usually prefer localhost")
            if re.search(r"(?i)(api key|subscription key).{0,20}(paste|send|email|screenshot)", line):
                print(f"WARN {rel}:{lineno}: check provider-key evidence wording: {line.strip()[:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
