#!/usr/bin/env python3
"""Summarize TowerScout Puppeteer browser smoke summary.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def tail(items, count=10):
    return items[-count:] if isinstance(items, list) else []


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_browser_run.py SUMMARY_JSON_OR_DIR", file=sys.stderr)
        return 2

    target = Path(sys.argv[1])
    summary_path = target / "summary.json" if target.is_dir() else target
    if not summary_path.exists():
        print(f"ERROR: summary not found: {summary_path}")
        return 1

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    print(f"summary: {summary_path}")
    for key in ("runId", "status", "provider", "baseUrl", "startedAt", "finishedAt"):
        print(f"{key}: {data.get(key)}")

    if data.get("error"):
        print(f"error: {data['error'].get('message')}")

    estimate = data.get("estimate") or {}
    if estimate:
        print(f"estimate: status={estimate.get('status')} tileCount={estimate.get('tileCount')} durationMs={estimate.get('durationMs')}")

    detection = data.get("detection") or {}
    if detection:
        print("detection: " + " ".join(
            f"{k}={detection.get(k)}" for k in (
                "detectionCount", "selectedCount", "listCount", "mapVisibleCount", "durationMs", "progressShown"
            )
        ))
        if detection.get("outputTail"):
            print("detection output tail:")
            for line in detection.get("outputTail", [])[-10:]:
                print(f"  {line}")

    cancel = data.get("cancel") or {}
    if cancel:
        print(f"cancel: abortStatus={cancel.get('abortStatus')} durationMs={cancel.get('durationMs')} detectionsAfterCancel={cancel.get('detectionCountAfterCancel')}")

    page_errors = data.get("pageErrors") or []
    console = data.get("browserConsole") or []
    network = data.get("network") or []
    bad_network = [n for n in network if isinstance(n, dict) and int(n.get("status") or 0) >= 400]

    print(f"pageErrors: {len(page_errors)}")
    for err in tail(page_errors, 5):
        print(f"  {err.get('message')}")

    warning_console = [c for c in console if c.get("type") in {"error", "warning"}]
    print(f"console warnings/errors: {len(warning_console)}")
    for item in tail(warning_console, 10):
        text = (item.get("text") or "").replace("\n", " ")[:250]
        print(f"  [{item.get('type')}] {text}")

    print(f"network status >=400: {len(bad_network)}")
    for item in tail(bad_network, 10):
        print(f"  {item.get('status')} {item.get('method')} {item.get('url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
