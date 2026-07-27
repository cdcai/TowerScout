from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_container_publish_sets_release_oci_label_build_args():
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")

    assert '--build-arg TOWERSCOUT_RELEASE_VERSION="$tag"' in workflow
    assert '--build-arg TOWERSCOUT_SOURCE_REF="$GITHUB_SHA"' in workflow


def test_container_publish_exposes_pytorch_flavor_input_and_build_arg():
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")

    assert "pytorch_flavor:" in workflow
    assert "- cuda126" in workflow
    assert 'pytorch_index_url="https://download.pytorch.org/whl/cu126"' in workflow
    assert '--build-arg PYTORCH_INDEX_URL="$pytorch_index_url"' in workflow
    assert '--build-arg TOWERSCOUT_PYTORCH_FLAVOR="$pytorch_flavor"' in workflow
    assert '--build-arg TOWERSCOUT_TORCH_VERSION="2.6.0"' in workflow
    assert '--build-arg TOWERSCOUT_TORCHVISION_VERSION="0.21.0"' in workflow
    assert 'published_tag="$tag-$pytorch_flavor"' in workflow
    assert 'tags=(--tag "$image:$published_tag")' in workflow
    assert 'tags+=(--tag "$image:latest-$pytorch_flavor")' in workflow
    assert "already ends with a different PyTorch flavor" in workflow
