"""Check public maintenance entrypoints without requiring private planning records."""
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
required = ("AGENTS.md", "CONTRIBUTING.md", "docs/maintenance.md")
missing = [p for p in required if not (root / p).is_file()]
if missing:
    print("Missing maintenance entrypoints: " + ", ".join(missing))
    raise SystemExit(1)
print("Public maintenance entrypoints exist")
