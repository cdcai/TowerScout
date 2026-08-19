"""Task-098/099/101 frontend dependency remediation contracts."""

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
PACKAGE_LOCK = REPO_ROOT / "package-lock.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task_101_puppeteer_and_node_baseline_are_exact() -> None:
    package = _read_json(PACKAGE_JSON)
    lock_root = _read_json(PACKAGE_LOCK)["packages"][""]

    assert package["devDependencies"] == {"puppeteer": "25.8.0"}
    assert package["engines"] == {"node": ">=22.12.0"}
    assert "overrides" not in package
    assert lock_root["devDependencies"] == package["devDependencies"]
    assert lock_root["engines"] == package["engines"]


def test_task_101_puppeteer_graph_removes_extract_zip() -> None:
    packages = _read_json(PACKAGE_LOCK)["packages"]

    assert not any(
        package_path == "node_modules/extract-zip"
        or package_path.endswith("/node_modules/extract-zip")
        for package_path in packages
    )
    for locked in packages.values():
        for dependency_group in (
            "dependencies",
            "optionalDependencies",
            "peerDependencies",
        ):
            assert "extract-zip" not in locked.get(dependency_group, {})

    puppeteer = packages["node_modules/puppeteer"]
    puppeteer_core = packages["node_modules/puppeteer-core"]
    browsers = packages["node_modules/@puppeteer/browsers"]
    assert puppeteer["version"] == "25.8.0"
    assert puppeteer["dev"] is True
    assert puppeteer["dependencies"]["@puppeteer/browsers"] == "3.2.1"
    assert puppeteer["dependencies"]["puppeteer-core"] == "25.8.0"
    assert puppeteer_core["version"] == "25.8.0"
    assert puppeteer_core["dev"] is True
    assert browsers["version"] == "3.2.1"
    assert browsers["dev"] is True
    assert browsers["engines"]["node"] == ">=22.12.0"
    assert "extract-zip" not in browsers.get("dependencies", {})


def test_prior_transitive_fixes_are_preserved_or_safely_removed() -> None:
    packages = _read_json(PACKAGE_LOCK)["packages"]

    # Puppeteer 25 removes these Task-099-era transitive paths entirely.
    for removed_path in (
        "node_modules/basic-ftp",
        "node_modules/ip-address",
        "node_modules/js-yaml",
    ):
        assert removed_path not in packages

    # The remaining websocket dependency advances beyond Task-099's fixed pin.
    ws = packages["node_modules/ws"]
    assert ws["version"] == "8.21.3"
    assert ws["dev"] is True
