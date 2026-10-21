"""Task-098 Slice F configuration-framework dependency contracts."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / "webapp" / "requirements.txt"


def _requirements() -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw_line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        package, version = line.split("==", maxsplit=1)
        pins[package.lower()] = version
    return pins


def test_qualified_configuration_framework_versions_are_pinned() -> None:
    pins = _requirements()

    assert pins["flask"] == "3.1.3"
    assert pins["python-dotenv"] == "1.2.2"
