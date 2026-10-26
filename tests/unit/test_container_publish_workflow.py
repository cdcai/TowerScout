from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_publication_uses_reviewed_main_and_safe_input_transport():
    workflow = yaml.safe_load((REPO_ROOT / '.github/workflows/container-publish.yml').read_text(encoding='utf-8'))
    job = workflow['jobs']['publish']
    assert job['if'] == "github.ref == 'refs/heads/main'"
    assert job['environment'] == 'official-release'
    steps = job['steps']
    checkout = steps[0]
    assert checkout['with'] == {'persist-credentials': False, 'ref': '${{ github.sha }}'}
    preflight = next(s for s in steps if s.get('name') == 'Validate approved publication inputs')
    build = next(s for s in steps if s.get('id') == 'build')
    assert steps.index(preflight) < steps.index(build)
    assert preflight['env']['EXPECTED_SOURCE'] == '${{ inputs.source_sha }}'
    assert 'validate_publish_inputs.py' in preflight['run']
    assert '/environments/official-release' in preflight['run']
    assert 'deployment-branch-policies' in preflight['run']
    for step in steps:
        assert '${{ inputs.' not in step.get('run', ''), step.get('name')


def test_all_workflow_checkouts_leave_credentials_unpersisted():
    for path in (REPO_ROOT / '.github/workflows').glob('*.yml'):
        workflow = yaml.safe_load(path.read_text(encoding='utf-8'))
        for job in workflow['jobs'].values():
            for step in job.get('steps', []):
                if step.get('uses', '').startswith('actions/checkout@'):
                    assert step['with']['persist-credentials'] is False, path.name


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
    assert "- cuda128" in workflow
    assert 'pytorch_index_url="https://download.pytorch.org/whl/cu128"' in workflow
    assert '--build-arg PYTORCH_INDEX_URL="$pytorch_index_url"' in workflow
    assert '--build-arg TOWERSCOUT_PYTORCH_FLAVOR="$pytorch_flavor"' in workflow
    assert '--build-arg TOWERSCOUT_TORCH_VERSION="2.10.0"' in workflow
    assert '--build-arg TOWERSCOUT_TORCHVISION_VERSION="0.25.0"' in workflow
    assert 'published_tag="$tag-$pytorch_flavor"' in workflow
    assert 'local_ref="$image:$published_tag"' in workflow
    assert (
        "LATEST_IMAGE: '${{ steps.build.outputs.image }}:latest-${{ steps.build.outputs.pytorch_flavor }}'"
        in workflow
    )
    assert "already ends with a different PyTorch flavor" in workflow
    # Generic tag guard: any -cuda<digits> suffix must match the selected
    # flavor, so a stale CUDA suffix fails instead of being re-suffixed.
    assert "*-cpu|*-cuda[0-9]*)" in workflow


def test_container_publish_gates_locally_before_login_or_push():
    workflow_text = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    steps = workflow["jobs"]["publish"]["steps"]
    names = [step.get("name") for step in steps]

    build = next(step for step in steps if step.get("id") == "build")["run"]
    assert "--load" in build
    assert "--provenance=false" in build
    assert "--push" not in build

    pre_scan = next(
        step
        for step in steps
        if step.get("name") == "Scan local image before publication"
    )
    assert pre_scan["with"]["severity"] == "CRITICAL,HIGH"
    assert pre_scan["with"]["ignore-unfixed"] == "false"
    assert pre_scan["with"]["exit-code"] == "0"
    assert "continue-on-error" not in pre_scan

    assert names.index("Enforce local pre-publication security gate") < names.index(
        "Log in to GHCR after local gate passes"
    )
    assert names.index("Log in to GHCR after local gate passes") < names.index(
        "Refuse to overwrite immutable version tag"
    )
    assert names.index("Refuse to overwrite immutable version tag") < names.index(
        "Push immutable versioned image and verify identity"
    )
    assert names.index(
        "Confirm exact-digest findings against approved policy"
    ) < names.index("Promote latest flavor tag")

    pre_gate = next(
        step for step in steps if step.get("id") == "prepublish-disposition"
    )["run"]
    assert (
        "--accepted-residuals .github/security/task103-accepted-residuals.v1.json"
        in pre_gate
    )
    assert "--expected-image-id '${{ steps.build.outputs.local_image_id }}'" in pre_gate
    assert "--candidate prepublish-image-trivy.json" in pre_gate

    assert ".trivyignore" not in workflow_text
    assert "--ignorefile" not in workflow_text
    assert "continue-on-error" not in workflow_text
    assert "ignore-unfixed: 'true'" not in workflow_text


def test_container_publish_refuses_to_overwrite_immutable_version_tag():
    workflow_text = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    steps = workflow["jobs"]["publish"]["steps"]
    guard = next(
        step
        for step in steps
        if step.get("name") == "Refuse to overwrite immutable version tag"
    )["run"]

    assert 'docker buildx imagetools inspect "$LOCAL_IMAGE"' in guard
    assert "Immutable version tag already exists" in guard
    assert "manifest unknown|not found" in guard
    assert "Could not prove that immutable version tag is absent" in guard
    assert workflow["concurrency"]["group"] == (
        "container-publish-${{ github.repository }}"
    )
    assert workflow["concurrency"]["cancel-in-progress"] is False


def test_container_publish_verifies_runtime_versions_and_remote_identity():
    workflow_path = REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    parsed_workflow = yaml.safe_load(workflow)
    boundary_step = next(
        step
        for step in parsed_workflow["jobs"]["publish"]["steps"]
        if step.get("name") == "Verify local dependency and geospatial boundary"
    )["run"]

    assert 'urllib3.__version__ == "2.8.0"' in workflow
    assert 'pip_urllib3.__version__ == "2.7.0"' in workflow
    assert "gdal-bin libgdal32 libheif1 python3.11" in workflow
    assert "site-packages/fiona.libs" in workflow
    assert "readlink -f" in workflow
    assert (
        "docker run --rm --entrypoint sh \"$LOCAL_IMAGE\" -s <<'CONTAINER_SH'"
        in boundary_step
    )
    assert boundary_step.count("CONTAINER_SH") == 2
    assert 'docker run --rm --entrypoint sh "$LOCAL_IMAGE" -c \'' not in boundary_step
    assert "awk '{print $3}'" in boundary_step
    assert 'test "$local_image_id" = "$local_manifest_digest"' not in workflow
    assert 'data.get("containerimage.config.digest")' in workflow
    assert "descriptor_config_digest" in workflow
    assert 'local_config_digest="$(docker image inspect' not in workflow
    assert "Could not resolve local image ID for $local_ref" in workflow
    assert "Could not resolve local manifest digest for $local_ref" in workflow
    # A registry push may translate OCI manifest media types to Docker schema
    # 2, changing only the manifest digest. Identity must therefore be proven
    # with the image config digest, while retaining both manifest digests as
    # evidence.
    assert 'test "$digest" = "$LOCAL_MANIFEST_DIGEST"' not in workflow
    assert 'test "$remote_config_digest" = "$LOCAL_CONFIG_DIGEST"' in workflow
    assert "local_manifest_digest" in workflow
    assert "local_config_digest" in workflow
    assert "remote-manifest.json" in workflow


def test_container_publish_scans_and_sboms_the_exact_published_digest():
    workflow = (
        REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
    ).read_text(encoding="utf-8")

    pinned_ref = "${{ steps.publish.outputs.pinned_ref }}"
    assert workflow.count(f"image-ref: '{pinned_ref}'") == 2
    assert "output: image-trivy.json" in workflow
    assert "format: cyclonedx" in workflow
    assert "output: image-sbom.cdx.json" in workflow
    assert "image-scan-dispositions.md" in workflow
    assert "scripts/task103_trivy_delta.py compare" in workflow
    assert "--baseline .github/security/task103-trivy-baseline.v1.json" in workflow
    assert (
        "--accepted-residuals .github/security/task103-accepted-residuals.v1.json"
        in workflow
    )
    assert "--candidate image-trivy.json" in workflow
    assert "--flavor '${{ steps.build.outputs.pytorch_flavor }}'" in workflow
    assert "--expected-image-id '${{ steps.build.outputs.local_image_id }}'" in workflow
    assert "image-scan-delta.json" in workflow
    assert ".github/security/task103-trivy-baseline.v1.json" in workflow
    assert ".github/security/task103-accepted-residuals.v1.json" in workflow
    assert "CRITICAL/HIGH findings are blocking" not in workflow
    assert "if: always()" in workflow


def test_container_verify_is_read_only_and_fails_closed_on_exact_identity():
    workflow_text = (
        REPO_ROOT / ".github" / "workflows" / "container-verify.yml"
    ).read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    steps = workflow["jobs"]["verify"]["steps"]
    identity = next(step for step in steps if step.get("id") == "identity")["run"]
    scan = next(
        step
        for step in steps
        if step.get("name") == "Scan exact published digest with Trivy"
    )
    disposition = next(
        step
        for step in steps
        if step.get("name") == "Confirm exact-digest findings against approved policy"
    )["run"]

    assert workflow["permissions"]["packages"] == "read"
    assert "docker push" not in workflow_text
    assert "latest-" not in workflow_text
    assert '"$image"@sha256:' in identity
    assert 'test "$remote_config_digest" = "$EXPECTED_CONFIG_DIGEST"' in identity
    assert 'test "$image_id" = "$EXPECTED_CONFIG_DIGEST"' in identity
    assert 'test "$source_label" = "$EXPECTED_SOURCE_REF"' in identity
    assert 'test "$flavor_label" = "$EXPECTED_FLAVOR"' in identity
    assert scan["with"]["severity"] == "CRITICAL,HIGH"
    assert scan["with"]["ignore-unfixed"] == "false"
    assert "--expected-image-id '${{ steps.identity.outputs.image_id }}'" in disposition
    assert '--source-ref "$EXPECTED_SOURCE_REF"' in disposition
    assert (
        "--accepted-residuals .github/security/task103-accepted-residuals.v1.json"
        in disposition
    )


def test_pip_inventory_is_bound_to_the_scanned_image_before_publication():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/container-publish.yml").read_text())
    steps = workflow["jobs"]["publish"]["steps"]
    boundary = next(step for step in steps if step.get("name") == "Verify local dependency and geospatial boundary")
    assert boundary["env"]["LOCAL_IMAGE_ID"] == "${{ steps.build.outputs.local_image_id }}"
    command = boundary["run"]
    assert '--entrypoint python "$LOCAL_IMAGE_ID" -I -B -' in command
    assert '--image-id "$LOCAL_IMAGE_ID" --source-ref "$GITHUB_SHA"' in command
    assert '--flavor "$PYTORCH_FLAVOR"' in command
    assert '--network none --read-only --user 0:0' in command
    assert '--cap-drop ALL --cap-add DAC_OVERRIDE' in command
    assert '< scripts/task104_urllib3_inventory.py > urllib3-inventory.json' in command
    names = [step.get("name") for step in steps]
    assert names.index(boundary["name"]) < names.index("Enforce local pre-publication security gate")
    for step in steps:
        if "task103_trivy_delta.py compare" in step.get("run", ""):
            assert "--urllib3-inventory urllib3-inventory.json" in step["run"]
            assert not step.get("continue-on-error", False)
    uploads = [step for step in steps if "upload-artifact@" in step.get("uses", "")]
    assert any("urllib3-inventory.json" in step["with"]["path"] for step in uploads)


def test_existing_digest_verification_collects_fresh_bound_inventory():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/container-verify.yml").read_text())
    steps = workflow["jobs"]["verify"]["steps"]
    inventory = next(step for step in steps if step.get("name") == "Verify exact-image pip inventory")
    assert inventory["env"]["IMAGE_ID"] == "${{ steps.identity.outputs.image_id }}"
    assert '--entrypoint python "$IMAGE_ID" -I -B -' in inventory["run"]
    assert '--image-id "$IMAGE_ID" --source-ref "$EXPECTED_SOURCE_REF"' in inventory["run"]
    assert '--flavor "$EXPECTED_FLAVOR"' in inventory["run"]
    assert '--network none --read-only --user 0:0' in inventory["run"]
    names = [step.get("name") for step in steps]
    assert names.index("Verify exact published identity and labels") < names.index(inventory["name"])
    assert names.index(inventory["name"]) < names.index("Confirm exact-digest findings against approved policy")
    gate = next(step for step in steps if step.get("name") == "Confirm exact-digest findings against approved policy")
    assert "--urllib3-inventory urllib3-inventory.json" in gate["run"]


def test_required_docker_build_exercises_inventory_without_publication():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/ci.yml").read_text())
    build = workflow["jobs"]["build"]
    assert build["name"] == "Full Docker build"
    steps = build["steps"]
    check = next(step for step in steps if step.get("name") == "Verify built-image pip inventory")
    assert not check.get("continue-on-error", False)
    assert not build.get("continue-on-error", False)
    assert '--entrypoint python "$image_id" -I -B -' in check["run"]
    assert '--image-id "$image_id" --source-ref "$GITHUB_SHA" --flavor cpu' in check["run"]
    assert 'docker push' not in str(build)
