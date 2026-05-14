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
    assert REQUIRED_COMPLIANCE_FILES.issubset(set(manifest["compliance_files"]))

    release_artifacts = manifest["release_artifacts"]
    for key in [
        "control_zip",
        "control_zip_sha256",
        "image",
        "image_digest",
        "asset_manifest",
        "asset_bundle_sha256",
    ]:
        assert key in release_artifacts

    source = manifest["corresponding_source"]
    assert "source_ref" in source
    assert "source_offer" in source
    assert "webapp/vendor/yolov5_local/" in source["required_paths"]

    yolo = manifest["runtime_components"]["yolo"]
    assert yolo["name"] == "Ultralytics YOLOv5"
    assert yolo["license"] == "AGPL-3.0"
    assert yolo["vendored_path"] == "webapp/vendor/yolov5_local"

    assert manifest["sbom"]["reference"] == "SBOM.txt"
    assert manifest["revocation"]["notes"]
