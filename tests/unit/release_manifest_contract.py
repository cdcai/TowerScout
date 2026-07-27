import re


REQUIRED_COMPLIANCE_FILES = {
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "MODEL_LICENSES.md",
    "DATA_LICENSES.md",
    "PROVIDER_TERMS.md",
    "SOURCE.txt",
    "SBOM.txt",
    "IMAGE.txt",
    "SHA256SUMS.txt",
}


def assert_manifest_schema(manifest):
    assert manifest["schema_version"] == 1
    assert manifest["track"] == "agpl-yolo"
    assert isinstance(manifest["release_version"], str)
    assert isinstance(manifest["release_statement"], str)
    assert manifest["asset_manifest"] == "webapp/asset_manifest.v1.json"
    assert manifest["pytorch_flavor"] in {"cpu", "cuda126"}
    assert REQUIRED_COMPLIANCE_FILES.issubset(set(manifest["compliance_files"]))

    release_artifacts = manifest["release_artifacts"]
    for key in [
        "control_zip",
        "control_zip_sha256",
        "control_zip_sha256_sidecar",
        "control_zip_sha256_reason",
        "image",
        "image_digest",
        "pytorch_flavor",
        "asset_manifest",
        "asset_bundle",
        "asset_bundle_sha256",
        "asset_bundle_sha256_sidecar",
        "asset_bundle_sha256_reason",
        "package_contents_sha256",
    ]:
        assert key in release_artifacts
    assert release_artifacts["pytorch_flavor"] == manifest["pytorch_flavor"]
    assert release_artifacts["package_contents_sha256"] == "SHA256SUMS.txt"
    if release_artifacts["control_zip"]:
        assert release_artifacts["control_zip_sha256_sidecar"].endswith(".zip.sha256")
    if release_artifacts["control_zip_sha256"]:
        assert re.fullmatch(r"[0-9a-f]{64}", release_artifacts["control_zip_sha256"])
    else:
        assert release_artifacts["control_zip_sha256_reason"]
    if release_artifacts["asset_bundle"]:
        assert release_artifacts["asset_bundle"].endswith(".zip")
        assert release_artifacts["asset_bundle_sha256_sidecar"].endswith(".zip.sha256")
    if release_artifacts["asset_bundle_sha256"]:
        assert re.fullmatch(r"[0-9a-f]{64}", release_artifacts["asset_bundle_sha256"])
    else:
        assert release_artifacts["asset_bundle_sha256_reason"]

    source = manifest["corresponding_source"]
    assert "source_ref" in source
    assert "source_offer" in source
    assert "webapp/vendor/yolov5_local/" in source["required_paths"]
    assert "compose.gpu.podman.yaml" in source["required_paths"]

    yolo = manifest["runtime_components"]["yolo"]
    assert yolo["name"] == "Ultralytics YOLOv5"
    assert yolo["license"] == "AGPL-3.0"
    assert yolo["vendored_path"] == "webapp/vendor/yolov5_local"

    assert manifest["sbom"]["reference"] == "SBOM.txt"
    assert manifest["revocation"]["notes"]
