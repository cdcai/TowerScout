from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_WORK = ROOT / ".agent_work"
TASKS_DIR = AGENT_WORK / "tasks"
ACTIVE_DIR = TASKS_DIR / "active"
COMPLETED_DIR = TASKS_DIR / "completed"
CONTEXT_ANALYSIS = AGENT_WORK / "context" / "analysis"
CONTEXT_STATUS = AGENT_WORK / "context" / "status"
README = AGENT_WORK / "README.md"
CURRENT_TASKS = AGENT_WORK / "current-tasks.md"

TASK_FILE_RE = re.compile(r"^TASK-(\d{3})-.*\.md$")
README_PATH_RE = re.compile(r"`(\.agent_work/[^`]+)`")


def parse_current_sprint_task_ids() -> set[str]:
    content = CURRENT_TASKS.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"### \*\*TASK-(\d{3}):", content))


def iter_task_markdown_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.iterdir() if path.is_file() and path.suffix == ".md")


def check_root_task_files(errors: list[str]) -> None:
    root_task_files = iter_task_markdown_files(TASKS_DIR)
    if root_task_files:
        errors.append(
            "Loose task files remain in `.agent_work/tasks/`: "
            + ", ".join(path.name for path in root_task_files)
        )


def check_active_and_completed_membership(errors: list[str]) -> None:
    current_ids = parse_current_sprint_task_ids()

    for path in iter_task_markdown_files(ACTIVE_DIR):
        match = TASK_FILE_RE.match(path.name)
        if not match:
            continue
        task_id = match.group(1)
        if task_id not in current_ids:
            errors.append(
                f"`tasks/active/` contains non-current-sprint task file `{path.name}`."
            )

    for path in iter_task_markdown_files(COMPLETED_DIR):
        match = TASK_FILE_RE.match(path.name)
        if not match:
            continue
        task_id = match.group(1)
        if task_id in current_ids:
            errors.append(
                f"`tasks/completed/` still contains current-sprint task file `{path.name}`."
            )


def check_status_for_raw_evidence(errors: list[str]) -> None:
    raw_suffixes = {".log", ".json", ".txt", ".png"}
    bad = sorted(
        path.name
        for path in CONTEXT_STATUS.iterdir()
        if path.is_file() and path.suffix.lower() in raw_suffixes
    )
    if bad:
        errors.append(
            "`context/status/` contains raw evidence files: " + ", ".join(bad)
        )


def check_analysis_for_task_scoped_files(errors: list[str]) -> None:
    bad = sorted(
        path.name
        for path in CONTEXT_ANALYSIS.iterdir()
        if path.is_file() and path.name.startswith("TASK-")
    )
    if bad:
        errors.append(
            "`context/analysis/` still contains task-scoped files: " + ", ".join(bad)
        )


def check_readme_paths(errors: list[str]) -> None:
    content = README.read_text(encoding="utf-8", errors="replace")
    for rel_path in sorted(set(README_PATH_RE.findall(content))):
        target = ROOT / rel_path.replace("/", "\\")
        if not target.exists():
            errors.append(f"README references missing path `{rel_path}`.")


def main() -> int:
    errors: list[str] = []
    check_root_task_files(errors)
    check_active_and_completed_membership(errors)
    check_status_for_raw_evidence(errors)
    check_analysis_for_task_scoped_files(errors)
    check_readme_paths(errors)

    if errors:
        print("validate_agent_work.py found issues:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("validate_agent_work.py passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
