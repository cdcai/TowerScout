#!/usr/bin/env python3
"""Prove the bounded pip/urllib3 inventory inside the exact candidate image.

Run through stdin with Python -I -B in an isolated, network-disabled container.
Only standard-library code is used; no application or provider configuration is
loaded. This supplements Trivy 0.69.3, whose embedded-SBOM findings omit PkgPath.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from email.parser import Parser
from pathlib import Path

SITE = "usr/local/lib/python3.11/site-packages"
APP_DIR = f"{SITE}/urllib3"
VENDOR_DIR = f"{SITE}/pip/_vendor/urllib3"
APP_METADATA = f"{SITE}/urllib3-2.8.0.dist-info/METADATA"
PIP_METADATA = f"{SITE}/pip-26.2.2.dist-info/METADATA"
VENDOR_SBOM = f"{SITE}/pip/_vendor/bom.cdx.json"
NOTICE_DIR = f"{SITE}/pip-26.2.2.dist-info/licenses/src/pip/_vendor/urllib3"
LOCATION_POLICY = "pip-vendored-urllib3-v1"
SCOPE = "image-root-excluding-dev-proc-sys"


class InventoryError(ValueError):
    """The exact inventory cannot establish the approved exception boundary."""


def _read_regular(root: Path, relative: str) -> str:
    path = root / relative
    if path.resolve(strict=True) != path or not path.is_file():
        raise InventoryError(f"expected a regular, non-redirected file: {relative}")
    return path.read_text(encoding="utf-8")


def _metadata_version(root: Path, relative: str, name: str) -> str:
    metadata = Parser().parsestr(_read_regular(root, relative))
    if metadata.get_all("Name") != [name] or len(metadata.get_all("Version", [])) != 1:
        raise InventoryError(f"invalid distribution metadata: {relative}")
    return metadata["Version"]


def _module_version(root: Path, relative: str) -> str:
    tree = ast.parse(_read_regular(root, f"{relative}/_version.py"))
    versions = [
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__version__"
            for target in node.targets
        )
    ]
    if len(versions) != 1 or not isinstance(versions[0], str):
        raise InventoryError(f"invalid urllib3 version declaration: {relative}")
    _read_regular(root, f"{relative}/__init__.py")
    return versions[0]


def _walk_error(error: OSError) -> None:
    raise error


def collect_inventory(root: Path) -> dict:
    root = root.resolve(strict=True)
    directories, distributions, sboms = [], [], []
    for directory, dirnames, filenames in os.walk(
        root, onerror=_walk_error, followlinks=False
    ):
        current = Path(directory)
        if current == root:
            dirnames[:] = [
                name for name in dirnames if name not in {"dev", "proc", "sys"}
            ]
        for name in dirnames:
            if name == "urllib3":
                path = current / name
                relative = path.relative_to(root).as_posix()
                if path.resolve(strict=True) != path:
                    raise InventoryError(f"redirected urllib3 directory: {relative}")
                directories.append(relative)
            if name.lower().startswith("urllib3-") and name.endswith(
                (".dist-info", ".egg-info")
            ):
                distributions.append((current / name).relative_to(root).as_posix())
        for name in filenames:
            path = current / name
            relative = path.relative_to(root).as_posix()
            # Include loose/egg module representations as unexpected copies.
            if name in {"urllib3.py", "urllib3.pyc"} or (
                name.lower().startswith("urllib3-")
                and name.endswith((".egg", ".egg-info", ".whl"))
            ):
                distributions.append(relative)
            if name.endswith((".cdx", ".cdx.json", ".spdx", ".spdx.json")):
                content = _read_regular(root, relative)
                if "urllib3" in content.lower():
                    sboms.append(relative)

    sbom_text = _read_regular(root, VENDOR_SBOM)
    sbom = json.loads(sbom_text)
    if sbom.get("bomFormat") != "CycloneDX":
        raise InventoryError("pip's embedded SBOM must be CycloneDX")
    components = sbom.get("components")
    if not isinstance(components, list):
        raise InventoryError("pip's embedded SBOM components are missing")
    matches = [
        component for component in components if component.get("name") == "urllib3"
    ]
    if (
        len(matches) != 1
        or matches[0].get("version") != "2.7.0"
        or matches[0].get("purl") != "pkg:pypi/urllib3@2.7.0"
    ):
        raise InventoryError("pip's embedded SBOM must identify exactly urllib3 2.7.0")

    notice_files = sorted(
        path.relative_to(root).as_posix() for path in (root / NOTICE_DIR).rglob("*")
    )
    _read_regular(root, f"{NOTICE_DIR}/LICENSE.txt")
    return {
        "scope": SCOPE,
        "urllib3_notice_files": notice_files,
        "urllib3_directories": sorted(directories),
        "urllib3_distributions": sorted(distributions),
        "urllib3_sbom_sources": sorted(sboms),
        "pip_version": _metadata_version(root, PIP_METADATA, "pip"),
        "application_version": _metadata_version(root, APP_METADATA, "urllib3"),
        "application_module_version": _module_version(root, APP_DIR),
        "vendored_module_version": _module_version(root, VENDOR_DIR),
        "vendored_sbom_sha256": hashlib.sha256(sbom_text.encode("utf-8")).hexdigest(),
    }


def validate_inventory(
    document: dict, image_id: str, source_ref: str, flavor: str
) -> None:
    expected = {
        "schema_version": 1,
        "location_policy": LOCATION_POLICY,
        "image_id": image_id,
        "source_ref": source_ref,
        "pytorch_flavor": flavor,
        "scope": SCOPE,
        "urllib3_directories": sorted([APP_DIR, VENDOR_DIR, NOTICE_DIR]),
        "urllib3_notice_files": [f"{NOTICE_DIR}/LICENSE.txt"],
        "urllib3_distributions": [f"{SITE}/urllib3-2.8.0.dist-info"],
        "urllib3_sbom_sources": [VENDOR_SBOM],
        "pip_version": "26.2.2",
        "application_version": "2.8.0",
        "application_module_version": "2.8.0",
        "vendored_module_version": "2.7.0",
    }
    if not isinstance(document, dict) or set(document) != set(expected) | {
        "vendored_sbom_sha256"
    }:
        raise InventoryError("urllib3 inventory has missing or unknown fields")
    for name, value in expected.items():
        if type(document[name]) is not type(value) or document[name] != value:
            raise InventoryError(f"urllib3 inventory mismatch: {name}")
    digest = document["vendored_sbom_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise InventoryError("urllib3 inventory requires the embedded SBOM SHA-256")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--flavor", required=True, choices=["cpu", "cuda128"])
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("inventory collection must run inside the Linux candidate image")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.image_id):
        parser.error("--image-id must be the inspected immutable image ID")
    try:
        document = {
            **collect_inventory(Path("/")),
            "schema_version": 1,
            "location_policy": LOCATION_POLICY,
            "image_id": args.image_id,
            "source_ref": args.source_ref,
            "pytorch_flavor": args.flavor,
        }
        validate_inventory(document, args.image_id, args.source_ref, args.flavor)
    except (
        InventoryError,
        OSError,
        ValueError,
        SyntaxError,
        TypeError,
        AttributeError,
    ) as exc:
        print(f"task104_urllib3_inventory: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
