"""Task-098 Slice E geospatial dependency and reader contracts."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / "webapp" / "requirements.txt"
ZIPCODE_MODULE = REPO_ROOT / "webapp" / "ts_zipcode.py"


def _requirements() -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw_line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        package, version = line.split("==", maxsplit=1)
        pins[package.lower()] = version
    return pins


def test_qualified_geospatial_pair_is_pinned() -> None:
    pins = _requirements()

    assert pins["fiona"] == "1.10.1"
    assert pins["geopandas"] == "1.1.2"


def test_zipcode_reader_preserves_explicit_fiona_backend() -> None:
    module = ZIPCODE_MODULE.read_text(encoding="utf-8")

    assert "gpd.read_file(zipcode_path, engine='fiona')" in module
