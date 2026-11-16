#!/usr/bin/env python3
"""Omit unsupported NIS functionality from the dedicated TowerScout image.

Run only during the reviewed Python 3.11 Linux image build. Package simulation
must match the complete non-essential removal set before any file is changed.
This does not prune arbitrary dependencies or alter the security acceptance gate.
"""

import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import sysconfig


PACKAGES = frozenset({
    "libnsl2", "libtirpc3", "libtirpc-common", "libgssapi-krb5-2",
    "libkrb5-3", "libk5crypto3", "libkrb5support0", "libkeyutils1",
})


def find_extension(directory):
    modules = list(directory.glob("nis.*.so"))
    if len(modules) != 1:
        raise RuntimeError("Expected exactly one NIS extension")
    module = modules[0]
    if not module.is_file() or module.is_symlink() or module.resolve() != module:
        raise RuntimeError("NIS extension must be a regular, non-redirected file")
    with module.open("rb") as stream:
        if stream.read(4) != b"\x7fELF":
            raise RuntimeError("NIS extension must be an ELF binary")
    return module


def validate_packages(status):
    rows = [line.split("\t") for line in status.splitlines()]
    if (
        len(rows) != len(PACKAGES)
        or any(len(row) != 3 for row in rows)
        or {row[0] for row in rows} != PACKAGES
        or any(row[1] not in ("", "no") or row[2] != "installed" for row in rows)
    ):
        raise RuntimeError("Removal packages must be exactly the non-essential installed set")


def validate_plan(plan):
    removals = re.findall(r"^(?:Purg|Remv) ([^ :]+)", plan, re.MULTILINE)
    if (
        len(removals) != len(PACKAGES)
        or set(removals) != PACKAGES
        or re.search(r"^Inst ", plan, re.MULTILINE)
    ):
        raise RuntimeError("APT simulation exceeded the reviewed removal set")


def main():
    if sys.platform != "linux" or sys.version_info[:2] != (3, 11) or os.geteuid() != 0:
        raise RuntimeError("NIS pruning requires the reviewed root Python 3.11 Linux image")
    module = find_extension(Path(sysconfig.get_path("stdlib")) / "lib-dynload")
    status = subprocess.check_output([
        "dpkg-query", "-W", "-f=${Package}\t${Essential}\t${db:Status-Status}\n",
        *sorted(PACKAGES),
    ], text=True)
    validate_packages(status)
    command = ["apt-get", "--no-auto-remove", "purge", *sorted(PACKAGES)]
    validate_plan(subprocess.check_output([command[0], "-s", *command[1:]], text=True))

    # The only Python ELF consumer of this chain in the reviewed image is NIS.
    # Omit that optional module as well, rather than leave a broken extension.
    module.unlink()
    subprocess.run([command[0], "-y", *command[1:]], check=True)
    subprocess.run(["apt-get", "check"], check=True)
    if subprocess.check_output(["dpkg", "--audit"], text=True).strip():
        raise RuntimeError("Package audit failed after NIS pruning")
    if importlib.util.find_spec("nis") is not None:
        raise RuntimeError("NIS remains importable after pruning")
    installed = subprocess.check_output([
        "dpkg-query", "-W", "-f=${Package}\t${db:Status-Status}\n",
    ], text=True)
    if any(
        line.split("\t")[0] in PACKAGES and line.endswith("\tinstalled")
        for line in installed.splitlines()
    ):
        raise RuntimeError("A pruned package remains installed")
    print("Omitted NIS and exactly eight non-essential packages; package audit passed")


if __name__ == "__main__":
    main()
