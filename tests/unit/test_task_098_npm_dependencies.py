"""Task-098/099 frontend transitive dependency remediation contracts."""

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
PACKAGE_LOCK = REPO_ROOT / "package-lock.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_puppeteer_direct_pin_is_unchanged() -> None:
    package = _read_json(PACKAGE_JSON)

    assert package["devDependencies"] == {"puppeteer": "24.19.0"}


def test_dependabot_transitive_fixes_are_locked_as_development_dependencies() -> None:
    packages = _read_json(PACKAGE_LOCK)["packages"]
    expected_versions = {
        "node_modules/basic-ftp": "5.3.1",
        "node_modules/ip-address": "10.3.1",
        "node_modules/js-yaml": "4.3.1",
        "node_modules/ws": "8.21.1",
    }

    for package_path, expected_version in expected_versions.items():
        locked = packages[package_path]
        assert locked["version"] == expected_version
        assert locked["dev"] is True
