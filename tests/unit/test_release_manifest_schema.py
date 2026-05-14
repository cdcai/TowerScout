import json
from pathlib import Path

from release_manifest_contract import assert_manifest_schema

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_checked_in_release_manifest_matches_v1_schema():
    manifest = json.loads(
        (REPO_ROOT / "release-manifest.v1.json").read_text(encoding="utf-8")
    )

    assert_manifest_schema(manifest)
