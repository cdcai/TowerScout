"""Filesystem and evidence regressions for the narrowly scoped pip inventory."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "task104_urllib3_inventory.py"
)
SPEC = importlib.util.spec_from_file_location("task104_urllib3_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)
IMAGE_ID = "sha256:" + "1" * 64


def _write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def image_root(tmp_path):
    for directory, version in [
        (inventory.APP_DIR, "2.8.0"),
        (inventory.VENDOR_DIR, "2.7.0"),
    ]:
        _write(
            tmp_path, f"{directory}/__init__.py", "from ._version import __version__\n"
        )
        _write(tmp_path, f"{directory}/_version.py", f'__version__ = "{version}"\n')
    _write(tmp_path, inventory.APP_METADATA, "Name: urllib3\nVersion: 2.8.0\n")
    _write(tmp_path, inventory.PIP_METADATA, "Name: pip\nVersion: 26.2.2\n")
    _write(
        tmp_path,
        inventory.VENDOR_SBOM,
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "components": [
                    {
                        "name": "urllib3",
                        "version": "2.7.0",
                        "purl": "pkg:pypi/urllib3@2.7.0",
                    }
                ],
            }
        ),
    )
    _write(
        tmp_path, f"{inventory.NOTICE_DIR}/LICENSE.txt", "Synthetic test license notice"
    )
    return tmp_path


def _document(root, flavor="cpu"):
    return {
        **inventory.collect_inventory(root),
        "schema_version": 1,
        "location_policy": inventory.LOCATION_POLICY,
        "image_id": IMAGE_ID,
        "source_ref": "test-source",
        "pytorch_flavor": flavor,
    }


@pytest.mark.parametrize("flavor", ["cpu", "cuda128"])
def test_accepts_only_the_expected_filesystem_inventory(image_root, flavor):
    document = _document(image_root, flavor)
    inventory.validate_inventory(document, IMAGE_ID, "test-source", flavor)
    assert len(document["vendored_sbom_sha256"]) == 64


@pytest.mark.parametrize(
    "relative,text",
    [
        ("app/unapproved/urllib3/__init__.py", ""),
        (f"{inventory.NOTICE_DIR}/unexpected.py", ""),
        ("tmp/urllib3-2.7.0.dist-info/METADATA", "Name: urllib3\nVersion: 2.7.0\n"),
        ("opt/urllib3.py", "__version__ = '2.7.0'"),
        ("opt/urllib3-2.7.0.whl", "unused wheel"),
        ("app/extra.cdx.json", '{"components":[{"name":"urllib3","version":"2.7.0"}]}'),
    ],
)
def test_rejects_extra_copies_or_ambiguous_sbom_sources(image_root, relative, text):
    _write(image_root, relative, text)
    document = _document(image_root)
    with pytest.raises(inventory.InventoryError, match="inventory mismatch"):
        inventory.validate_inventory(document, IMAGE_ID, "test-source", "cpu")


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-vendor",
        "wrong-app-version",
        "wrong-pip-version",
        "wrong-sbom-version",
        "duplicate-sbom-component",
        "unknown-proof-field",
        "missing-proof-field",
        "wrong-image",
        "wrong-source",
        "wrong-flavor",
        "wrong-scope",
        "invalid-sbom-hash",
    ],
)
def test_rejects_incomplete_or_changed_inventory(image_root, mutation):
    if mutation == "missing-vendor":
        (image_root / inventory.VENDOR_DIR / "_version.py").unlink()
    elif mutation == "wrong-app-version":
        _write(image_root, inventory.APP_METADATA, "Name: urllib3\nVersion: 2.7.0\n")
    elif mutation == "wrong-pip-version":
        _write(image_root, inventory.PIP_METADATA, "Name: pip\nVersion: 99.0\n")
    elif mutation in {"wrong-sbom-version", "duplicate-sbom-component"}:
        path = image_root / inventory.VENDOR_SBOM
        sbom = json.loads(path.read_text())
        if mutation == "wrong-sbom-version":
            sbom["components"][0]["version"] = "2.6.0"
        else:
            sbom["components"].append(sbom["components"][0].copy())
        path.write_text(json.dumps(sbom))
    with pytest.raises((inventory.InventoryError, FileNotFoundError)):
        document = _document(image_root)
        changes = {
            "unknown-proof-field": ("unexpected", True),
            "wrong-image": ("image_id", "sha256:" + "2" * 64),
            "wrong-source": ("source_ref", "other-source"),
            "wrong-flavor": ("pytorch_flavor", "cuda128"),
            "wrong-scope": ("scope", "site-packages-only"),
            "invalid-sbom-hash": ("vendored_sbom_sha256", "not-a-hash"),
        }
        if mutation in changes:
            key, value = changes[mutation]
            document[key] = value
        elif mutation == "missing-proof-field":
            del document["urllib3_directories"]
        inventory.validate_inventory(document, IMAGE_ID, "test-source", "cpu")


def test_filesystem_read_errors_are_not_silently_ignored(image_root, monkeypatch):
    def failing_walk(root, *, onerror, followlinks):
        onerror(PermissionError("incomplete inventory"))
        return iter([])

    monkeypatch.setattr(inventory.os, "walk", failing_walk)
    with pytest.raises(PermissionError, match="incomplete inventory"):
        inventory.collect_inventory(image_root)
