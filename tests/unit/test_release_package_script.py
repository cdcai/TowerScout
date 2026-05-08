import shutil
import subprocess
import uuid
import os
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"

pytestmark = pytest.mark.skipif(
    os.name != "nt",
    reason="package-release.ps1 is a Windows release helper validated on Windows",
)


def _run_package_release(*args):
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT),
            *args,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_package_release_requires_digest_by_default():
    result = _run_package_release(
        "-Version",
        f"pytest-no-digest-{uuid.uuid4().hex}",
        "-OutputDir",
        ".agent_work\\pytest-temp\\package-release-no-digest",
        "-Image",
        "ghcr.io/j-schulein/towerscout",
        "-NoZip",
        "-Force",
    )

    assert result.returncode != 0
    assert "Release packaging requires -ImageDigest" in (result.stderr + result.stdout)


def test_package_release_stages_digest_pinned_image():
    package_id = f"pytest-digest-{uuid.uuid4().hex}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    digest = "sha256:" + ("1" * 64)
    try:
        result = _run_package_release(
            "-Version",
            package_id,
            "-OutputDir",
            str(output_dir),
            "-Image",
            "ghcr.io/j-schulein/towerscout",
            "-ImageDigest",
            digest,
            "-NoZip",
            "-Force",
        )

        assert result.returncode == 0, result.stderr + result.stdout
        stage_path = output_path / f"towerscout-{package_id}"
        env_example = (stage_path / ".env.example").read_text(encoding="utf-8")
        image_txt = (stage_path / "IMAGE.txt").read_text(encoding="utf-8")
        assert f"TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout@{digest}" in env_example
        assert f"TOWERSCOUT_IMAGE_DIGEST={digest}" in env_example
        assert f"Image: ghcr.io/j-schulein/towerscout@{digest}" in image_txt
    finally:
        shutil.rmtree(output_path, ignore_errors=True)
