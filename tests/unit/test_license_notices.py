import json
import hashlib
import importlib.util
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_current_yolo_notice_is_agpl_not_mit():
    third_party = (REPO_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")

    assert "Ultralytics YOLOv5" in third_party
    assert "AGPL-3.0" in third_party
    assert "YOLO | MIT" not in third_party


def test_release_compliance_payload_files_exist():
    required_files = [
        "LICENSE",
        "licenses/Apache-2.0.txt",
        "licenses/AGPL-3.0.txt",
        "licenses/CC-BY-NC-SA-4.0.txt",
        "licenses/TowerScout-APPLICATION-GRANT.md",
        "licenses/jQuery-MIT.txt",
        "licenses/SyntheticData-MIT.txt",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "MODEL_LICENSES.md",
        "DATA_LICENSES.md",
        "PROVIDER_TERMS.md",
        "SOURCE.txt",
        "SBOM.txt",
        "release-manifest.v1.json",
    ]

    for relative_path in required_files:
        assert (REPO_ROOT / relative_path).is_file()


def test_legacy_root_license_txt_is_quarantined():
    assert not (REPO_ROOT / "LICENSE.TXT").exists()
    assert (REPO_ROOT / "docs" / "legacy" / "LEGACY-LICENSE-NOTICE.md").is_file()


def test_package_metadata_points_to_composite_license_file():
    package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    package_lock = json.loads(
        (REPO_ROOT / "package-lock.json").read_text(encoding="utf-8")
    )

    assert package_json["license"] == "SEE LICENSE IN LICENSE"
    assert package_lock["packages"][""]["license"] == "SEE LICENSE IN LICENSE"


def test_license_notice_route_is_visible_in_app_shell():
    template = (
        REPO_ROOT / "webapp" / "templates" / "towerscout.html"
    ).read_text(encoding="utf-8")

    assert 'href="/license"' in template
    assert "Source/licenses" in template


def test_full_license_texts_preserve_reviewed_upstream_bytes():
    apache = (REPO_ROOT / "licenses/Apache-2.0.txt").read_bytes()
    assert hashlib.sha256(apache).hexdigest() == (
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    )
    assert (REPO_ROOT / "licenses/AGPL-3.0.txt").read_bytes() == (
        REPO_ROOT / "webapp/vendor/yolov5_local/LICENSE"
    ).read_bytes()
    assert (REPO_ROOT / "licenses/CC-BY-NC-SA-4.0.txt").read_bytes() == (
        REPO_ROOT / "docs/legacy/LICENSE-CC-BY-NC-SA-4.0.txt"
    ).read_bytes()


def test_container_source_notice_uses_only_immutable_refs_for_downloads():
    spec = importlib.util.spec_from_file_location(
        "source_notice", REPO_ROOT / "scripts/write-source-notice.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source_ref = "a" * 40
    notice = module.source_notice(source_ref)
    assert f"https://github.com/cdcai/TowerScout/tree/{source_ref}" in notice
    assert f"https://github.com/cdcai/TowerScout/archive/{source_ref}.tar.gz" in notice
    for local_ref in ("unknown", "local-review", "", "a" * 39, "main", "x\nSource URL: forged"):
        notice = module.source_notice(local_ref)
        assert "LOCAL VALIDATION ONLY" in notice
        assert "\nSource URL:" not in notice
        assert "/archive/" not in notice


def test_container_includes_license_payload_and_generates_source_notice():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY licenses licenses" in dockerfile
    assert 'RUN python scripts/write-source-notice.py --source-ref "${TOWERSCOUT_SOURCE_REF}" --output SOURCE.txt' in dockerfile


def test_application_grant_covers_inherited_sources_and_excludes_third_party_assets():
    grant = (REPO_ROOT / "licenses/TowerScout-APPLICATION-GRANT.md").read_text(encoding="utf-8")
    block = re.search(r"```text\n(.*?)\n```", grant, re.DOTALL)
    assert block is not None
    paths = block.group(1).splitlines()
    assert len(paths) == len(set(paths))
    assert "AGPL-3.0-only" in grant
    assert "not revoked" in grant
    assert "weights** retain CC-BY-NC-SA-4.0" in grant

    for path in paths:
        assert path.startswith("webapp/")
        assert ".." not in Path(path).parts
        assert "/vendor/" not in path
        assert "/model_params/" not in path
        assert "/data/" not in path
        assert path != "webapp/js/jquery-3.5.1.min.js"
        assert (REPO_ROOT / path).is_file()

    # Previously changed headers and extracted modules must be covered too.
    assert {"webapp/towerscout.py", "webapp/templates/towerscout.html",
            "webapp/js/towerscout.js", "webapp/js/towerscout.original.js"}.issubset(paths)
    # Catch new application modules omitted from the human-readable inventory.
    application = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / 'webapp').rglob('*')
        if path.is_file() and path.suffix in {'.py', '.js', '.css', '.html'}
        and 'vendor' not in path.relative_to(REPO_ROOT / 'webapp').parts
        and path.name != 'jquery-3.5.1.min.js'
        and '__pycache__' not in path.parts
    }
    assert application == set(paths)
    build = (REPO_ROOT / "webapp/build.js").read_text(encoding="utf-8")
    module_order = build.split("const MODULE_ORDER = [", 1)[1].split("];", 1)[0]
    for module in re.findall(r"'([^']+\.js)'", module_order):
        assert "webapp/js/" + module in paths
    for path in paths:
        header = (REPO_ROOT / path).read_text(encoding="utf-8-sig")[:2000]
        if "Licensed under CC-BY-NC-SA-4.0" in header:
            assert "CC-BY-NC-SA-4.0 OR AGPL-3.0-only" in header


def test_modified_vendor_files_and_adapted_defaults_carry_notices():
    modified = ['models/common.py', 'models/experimental.py', 'models/yolo.py',
                'utils/__init__.py', 'utils/augmentations.py', 'utils/autoanchor.py',
                'utils/dataloaders.py', 'utils/downloads.py', 'utils/general.py',
                'utils/metrics.py', 'utils/plots.py', 'utils/torch_utils.py']
    for relative in modified:
        header = (REPO_ROOT / 'webapp/vendor/yolov5_local' / relative).read_text(encoding='utf-8')[:400]
        assert 'Modified for TowerScout' in header
        assert '2026' in header and 'AGPL-3.0' in header
    defaults = (REPO_ROOT / 'SyntheticData/defaults.py').read_text(encoding='utf-8')
    assert 'Copyright (c) 2017 Debidatta Dwibedi' in defaults
    assert 'licenses/SyntheticData-MIT.txt' in defaults
