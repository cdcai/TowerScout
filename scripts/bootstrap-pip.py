#!/usr/bin/env python3
"""Install reviewed pip bytes before any dependency resolution.

Hash independently published by the Python security team and PyPI:
https://discuss.python.org/t/109576
https://pypi.org/pypi/pip/26.2.2/json
Uses stdlib TLS plus a mandatory artifact hash, then installs offline.
Run with the target virtual environment's Python; never changes other envs.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request

WHEEL_NAME = "pip-26.2.2-py3-none-any.whl"
WHEEL_URL = "https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/" + WHEEL_NAME
WHEEL_SHA256 = "fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
MAX_WHEEL_BYTES = 8 * 1024 * 1024


def bootstrap(parent: Path | None = None) -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("Secure pip bootstrap requires Python 3.10+; the supported Podman prerequisite is 64-bit Python 3.12.")
    # Respect an explicitly approved build CA without disabling verification.
    context = ssl.create_default_context()
    if os.environ.get("PIP_CERT"):
        context.load_verify_locations(cafile=os.environ["PIP_CERT"])
    with tempfile.TemporaryDirectory(prefix="towerscout-pip-", dir=parent) as staging:
        wheel = Path(staging) / WHEEL_NAME
        digest = hashlib.sha256()
        size = 0
        deadline = time.monotonic() + 120
        with urllib.request.urlopen(WHEEL_URL, context=context, timeout=30) as response, wheel.open("xb") as output:
            while chunk := response.read(65536):
                if time.monotonic() > deadline:
                    raise TimeoutError("pip bootstrap download deadline exceeded")
                size += len(chunk)
                if size > MAX_WHEEL_BYTES:
                    raise ValueError("pip bootstrap download exceeds size limit")
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != WHEEL_SHA256:
            raise ValueError("pip bootstrap SHA-256 mismatch; no installation performed")
        subprocess.run(
            [sys.executable, "-I", "-m", "pip", "--isolated", "--disable-pip-version-check",
             "install", "--no-index", "--no-deps", "--no-cache-dir", "--force-reinstall", str(wheel)],
            check=True, timeout=180,
        )


if __name__ == "__main__":
    bootstrap()
