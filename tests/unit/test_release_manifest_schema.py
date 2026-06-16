import json
import subprocess
import sys
from pathlib import Path

from release_manifest_contract import assert_manifest_schema

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "towerscout-release-candidate-gate"
    / "scripts"
    / "check_release_manifest.py"
)


def test_checked_in_release_manifest_matches_v1_schema():
    manifest = json.loads(
        (REPO_ROOT / "release-manifest.v1.json").read_text(encoding="utf-8")
    )

    assert_manifest_schema(manifest)


def test_release_manifest_checker_accepts_v1_snake_case_schema(tmp_path):
    release_root = tmp_path / "release"
    release_root.mkdir()
    (release_root / "SHA256SUMS.txt").write_text("placeholder\n", encoding="utf-8")
    manifest = json.loads(
        (REPO_ROOT / "release-manifest.v1.json").read_text(encoding="utf-8")
    )
    digest = "sha256:" + ("a" * 64)
    manifest["release_version"] = "v0.1.0-rc5-test"
    manifest["image"] = f"ghcr.io/j-schulein/towerscout:v0.1.0-rc5-test-cuda121@{digest}"
    manifest["image_digest"] = digest
    manifest["corresponding_source"]["source_ref"] = "b" * 40
    manifest["release_artifacts"]["image"] = manifest["image"]
    manifest["release_artifacts"]["image_digest"] = digest
    manifest["release_artifacts"]["package_contents_sha256"] = "SHA256SUMS.txt"
    manifest_path = release_root / "release-manifest.v1.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CHECKER), str(manifest_path), str(release_root)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "WARN:" not in result.stdout
