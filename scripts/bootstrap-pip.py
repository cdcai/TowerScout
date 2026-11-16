#!/usr/bin/env python3
"""Install reviewed pip bytes before any dependency resolution.

Reviewed wheel hash and release provenance published by PyPI:
https://pypi.org/project/pip/26.3/
https://pypi.org/pypi/pip/26.3/json
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

WHEEL_NAME = "pip-26.3-py3-none-any.whl"
WHEEL_URL = "https://files.pythonhosted.org/packages/07/25/ee8c38ae72d66b844ce8eb9711ba905dba21ca1a8a0c960057c41cd23337/" + WHEEL_NAME
WHEEL_SHA256 = "f3b60b20ffaadd4415ed7957212a38ac63fa4c5fa375bd0f4a797777940fad13"
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
