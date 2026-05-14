#!/usr/bin/env python3
"""Heuristic scan for sensitive TowerScout terms in tracked-ish files."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
TERMS = [
    "GOOGLE_API_KEY",
    "AZURE_MAPS_SUBSCRIPTION_KEY",
    "AZURE_MAPS_KEY",
    "BING_API_KEY",
    "FLASK_SECRET_KEY",
    "apikey",
    "subscriptionKey",
    "AIza",
    "AccountKey=",
]
TEXT_SUFFIXES = {".py", ".js", ".json", ".md", ".txt", ".yml", ".yaml", ".ps1", ".cmd", ".bat", ".env", ".example"}


def should_scan(path: Path) -> bool:
    try:
        relative_parts = path.relative_to(ROOT).parts
    except ValueError:
        relative_parts = path.parts
    if any(part in SKIP_DIRS for part in relative_parts[:-1]):
        return False
    if path.name.startswith(".env"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def main() -> int:
    count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            low = line.lower()
            hits = [term for term in TERMS if term.lower() in low]
            if hits:
                count += 1
                rel = path.relative_to(ROOT)
                snippet = line.strip()[:220]
                print(f"{rel}:{lineno}: {', '.join(hits)}: {snippet}")
    print(f"matches: {count}")
    print("Review matches manually. Environment variable names and safe examples may be expected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
