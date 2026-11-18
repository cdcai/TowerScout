"""Exercise CI browser selection without downloading or launching Chromium."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/task-087-frontend-puppeteer.yml"


def _bash():
    if os.name == "nt":
        git = shutil.which("git")
        candidate = Path(git).resolve().parents[1] / "bin/bash.exe" if git else None
        if candidate and candidate.is_file():
            return str(candidate)
        pytest.skip("Git Bash is required for the Windows shell regression check")
    executable = shutil.which("bash")
    if not executable:
        pytest.skip("Bash is required for the CI shell regression check")
    return executable


@pytest.mark.parametrize("job", ["production-controller", "puppeteer-e2e"])
@pytest.mark.parametrize("layout", ["chrome-linux", "chrome-linux64"])
@pytest.mark.parametrize("browser_present", [True, False])
def test_chromium_selection_ignores_helpers(tmp_path, job, layout, browser_present):
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    step = next(
        step for step in workflow["jobs"][job]["steps"]
        if step.get("name") == "Install Playwright Chromium for Puppeteer"
    )
    home = tmp_path / "home with spaces"
    cache = home / ".cache/ms-playwright/chromium-fixture" / layout
    cache.mkdir(parents=True)
    # Helpers are deliberately created first, reproducing the prefix-match trap.
    names = ["chrome_crashpad_handler", "chrome_proxy", "chrome-headless-shell"]
    if browser_present:
        names.append("chrome")
    for name in names:
        executable = cache / name
        executable.write_text("#!/bin/sh\nprintf 'Chromium fixture\\n'\n", encoding="utf-8")
        executable.chmod(0o755)
    environment_file = tmp_path / "github-env"
    environment_file.write_text("EXISTING_VALUE=preserved\n", encoding="utf-8")
    environment = os.environ.copy()
    environment.update(HOME=home.as_posix(), GITHUB_ENV=environment_file.as_posix())
    # Stub installation only; execute the workflow's real selection/export shell.
    command = "npx() { return 0; }\n" + step["run"]
    result = subprocess.run(
        [_bash(), "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", command],
        env=environment, capture_output=True, text=True, timeout=20,
    )
    lines = environment_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "EXISTING_VALUE=preserved"
    if browser_present:
        assert result.returncode == 0, result.stderr
        assert len(lines) == 2
        key, selected = lines[1].split("=", 1)
        assert key == "PUPPETEER_EXECUTABLE_PATH"
        # Git Bash normalizes HOME from C:/... to /c/... on Windows.
        if os.name == "nt" and len(selected) > 3 and selected[0] == "/" and selected[2] == "/":
            selected = selected[1] + ":" + selected[2:]
        assert Path(selected).resolve() == (cache / "chrome").resolve()
    else:
        assert result.returncode != 0
        assert len(lines) == 1, "Missing Chromium must not export a helper executable"
