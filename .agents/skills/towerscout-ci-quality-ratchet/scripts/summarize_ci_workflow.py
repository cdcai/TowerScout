#!/usr/bin/env python3
"""Lightweight GitHub Actions workflow summary without external YAML deps."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_ci_workflow.py WORKFLOW_YML", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: not found: {path}")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    print(f"workflow: {path}")
    name = re.search(r"(?m)^name:\s*(.+)$", text)
    if name:
        print(f"name: {name.group(1).strip()}")
    jobs = re.findall(r"(?m)^  ([A-Za-z0-9_-]+):\s*$", text)
    print("jobs:")
    for job in jobs:
        print(f"  {job}")
    print("continue-on-error lines:")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "continue-on-error" in line:
            print(f"  {lineno}: {line.strip()}")
    print("uses refs:")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "uses:" in line:
            print(f"  {lineno}: {line.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
