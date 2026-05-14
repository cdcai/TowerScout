import shutil
import subprocess
import uuid
import os
import json
from pathlib import Path

import pytest

from release_manifest_contract import (
    REQUIRED_COMPLIANCE_FILES,
    assert_manifest_schema,
)


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


def test_package_release_rejects_dirty_source_by_default():
    package_id = f"pytest-dirty-{uuid.uuid4().hex}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    digest = "sha256:" + ("2" * 64)
    dirty_marker = REPO_ROOT / "tests" / "unit" / f"dirty-marker-{uuid.uuid4().hex}.txt"
    try:
        dirty_marker.write_text("dirty tree marker", encoding="utf-8")
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

        assert result.returncode != 0
        assert "Release packaging requires a clean git working tree" in (
            result.stderr + result.stdout
        )
    finally:
        dirty_marker.unlink(missing_ok=True)
        shutil.rmtree(output_path, ignore_errors=True)


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
            "-AllowDirtySource",
            "-NoZip",
            "-Force",
        )

        assert result.returncode == 0, result.stderr + result.stdout
        stage_path = output_path / f"towerscout-{package_id}"
        env_example = (stage_path / ".env.example").read_text(encoding="utf-8")
        image_txt = (stage_path / "IMAGE.txt").read_text(encoding="utf-8")
        asset_readme = (stage_path / "assets" / "README.txt").read_text(encoding="utf-8")
        release_manifest = json.loads(
            (stage_path / "release-manifest.v1.json").read_text(encoding="utf-8")
        )
        assert_manifest_schema(release_manifest)
        assert f"TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout@{digest}" in env_example
        assert f"TOWERSCOUT_IMAGE_DIGEST={digest}" in env_example
        assert f"Image: ghcr.io/j-schulein/towerscout@{digest}" in image_txt
        assert release_manifest["track"] == "agpl-yolo"
        assert release_manifest["image_digest"] == digest
        assert release_manifest["release_artifacts"]["image_digest"] == digest
        assert release_manifest["release_artifacts"]["control_zip"] == ""
        assert REQUIRED_COMPLIANCE_FILES.issubset(
            set(release_manifest["compliance_files"])
        )
        assert release_manifest["corresponding_source"]["source_ref"]
        assert (
            release_manifest["runtime_components"]["yolo"]["license"]
            == "AGPL-3.0"
        )
        assert release_manifest["sbom"]["reference"] == "SBOM.txt"
        assert "scripts\\import-assets.cmd -Source assets\n" in asset_readme
        assert (
            "scripts\\import-assets.cmd -Source assets -VerifyHashes" in asset_readme
        )
        assert "YOLO-derived/AGPL-governed" in asset_readme
        for relative_path in [
            "LICENSE",
            "NOTICE",
            "THIRD_PARTY_NOTICES.md",
            "MODEL_LICENSES.md",
            "DATA_LICENSES.md",
            "PROVIDER_TERMS.md",
            "SOURCE.txt",
            "SBOM.txt",
            "release-manifest.v1.json",
        ]:
            assert (stage_path / relative_path).is_file()
        assert (stage_path / "docs" / "release-asset-bundle-contract.md").is_file()
    finally:
        shutil.rmtree(output_path, ignore_errors=True)
