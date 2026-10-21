#!/usr/bin/env python3
"""Quick checks for TowerScout .agent_work hygiene."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
AGENT = ROOT / ".agent_work"


def main() -> int:
    warnings: list[str] = []
    if not AGENT.exists():
        print(f"ERROR: .agent_work not found under {ROOT}")
        return 1

    task_root = AGENT / "tasks"
    if task_root.exists():
        loose = sorted(p.name for p in task_root.glob("*.md"))
        if loose:
            warnings.append("Loose task markdown files in .agent_work/tasks: " + ", ".join(loose))

    status = AGENT / "context" / "status"
    if status.exists():
        raw = sorted(p.name for p in status.iterdir() if p.is_file() and p.suffix.lower() in {".log", ".json", ".txt", ".png"})
        if raw:
            warnings.append("Raw evidence-like files in context/status: " + ", ".join(raw))

    validator = AGENT / "scripts" / "validate_agent_work.py"
    if validator.exists():
        print("running .agent_work validator...")
        proc = subprocess.run([sys.executable, str(validator)], cwd=str(ROOT), text=True, capture_output=True)
        print(proc.stdout.strip())
        if proc.stderr.strip():
            print(proc.stderr.strip())
        if proc.returncode != 0:
            warnings.append(f"validate_agent_work.py exited with {proc.returncode}")
    else:
        warnings.append(".agent_work/scripts/validate_agent_work.py not found")

    for item in warnings:
        print(f"WARN: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
