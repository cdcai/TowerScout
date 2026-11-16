"""Fail-closed preflight checks for the narrowly bounded image-build removal."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "prune-runtime-nis.py"
SPEC = importlib.util.spec_from_file_location("prune_runtime_nis", SCRIPT)
prune = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prune)


def status_rows():
    return [f"{name}\tno\tinstalled" for name in sorted(prune.PACKAGES)]


@pytest.mark.parametrize("mutation", ["essential", "missing", "extra", "duplicate", "not-installed"])
def test_rejects_unreviewed_package_metadata(mutation):
    rows = status_rows()
    if mutation == "essential":
        rows[0] = rows[0].replace("\tno\t", "\tyes\t")
    elif mutation == "missing":
        rows.pop()
    elif mutation == "extra":
        rows.append("login\tyes\tinstalled")
    elif mutation == "duplicate":
        rows[-1] = rows[0]
    else:
        rows[0] = rows[0].replace("\tinstalled", "\tconfig-files")
    with pytest.raises(RuntimeError, match="non-essential installed set"):
        prune.validate_packages("\n".join(rows))


@pytest.mark.parametrize("extra", ["Purg login [1]", "Remv libsqlite3-0 [1]", "Inst replacement [1]"])
def test_rejects_unexpected_apt_actions(extra):
    plan = "\n".join(f"Purg {name} [1]" for name in sorted(prune.PACKAGES))
    with pytest.raises(RuntimeError, match="reviewed removal set"):
        prune.validate_plan(plan + "\n" + extra)


def test_exact_package_preflight_is_accepted():
    prune.validate_packages("\n".join(status_rows()))
    prune.validate_plan("\n".join(f"Purg {name} [1]" for name in sorted(prune.PACKAGES)))


def test_extension_preflight_requires_one_real_elf(tmp_path):
    with pytest.raises(RuntimeError, match="exactly one"):
        prune.find_extension(tmp_path)
    module = tmp_path / "nis.fixture.so"
    module.write_bytes(b"not an ELF")
    with pytest.raises(RuntimeError, match="ELF"):
        prune.find_extension(tmp_path)
    module.write_bytes(b"\x7fELFfixture")
    assert prune.find_extension(tmp_path) == module
    (tmp_path / "nis.extra.so").write_bytes(b"\x7fELFfixture")
    with pytest.raises(RuntimeError, match="exactly one"):
        prune.find_extension(tmp_path)


def test_preflight_refuses_a_host_platform(monkeypatch):
    monkeypatch.setattr(prune.sys, "platform", "win32")
    monkeypatch.setattr(prune.subprocess, "run", lambda *a, **k: pytest.fail("mutation attempted"))
    with pytest.raises(RuntimeError, match="Python 3.11 Linux"):
        prune.main()


def test_unexpected_removal_fails_before_extension_or_system_mutation(tmp_path, monkeypatch):
    directory = tmp_path / "lib-dynload"
    directory.mkdir()
    module = directory / "nis.fixture.so"
    module.write_bytes(b"\x7fELFfixture")
    answers = iter([
        "\n".join(status_rows()),
        "\n".join(f"Purg {name} [1]" for name in sorted(prune.PACKAGES))
        + "\nRemv login [1]",
    ])
    monkeypatch.setattr(prune, "sys", SimpleNamespace(platform="linux", version_info=(3, 11)))
    monkeypatch.setattr(prune, "os", SimpleNamespace(geteuid=lambda: 0))
    monkeypatch.setattr(prune, "sysconfig", SimpleNamespace(get_path=lambda name: str(tmp_path)))
    monkeypatch.setattr(prune, "subprocess", SimpleNamespace(
        check_output=lambda *a, **k: next(answers),
        run=lambda *a, **k: pytest.fail("system mutation attempted"),
    ))
    with pytest.raises(RuntimeError, match="reviewed removal set"):
        prune.main()
    assert module.read_bytes() == b"\x7fELFfixture"
