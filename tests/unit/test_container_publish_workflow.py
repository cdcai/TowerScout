from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_container_publish_sets_release_oci_label_build_args():
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")

    assert '--build-arg TOWERSCOUT_RELEASE_VERSION="$tag"' in workflow
    assert '--build-arg TOWERSCOUT_SOURCE_REF="$GITHUB_SHA"' in workflow
