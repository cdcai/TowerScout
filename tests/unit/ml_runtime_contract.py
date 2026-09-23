"""Shared TASK-103 ML runtime contract for tests.

The production files (webapp/requirements.txt, Dockerfile, compose.build.yaml,
.env.example, the container-publish workflow, the launcher library, the
packaging script and the qualification harness) each write these values
literally. ``test_task_103_ml_runtime_contract.py`` checks that every one of
them agrees with the constants below, so a version or flavor move changes this
module plus the production files, and nothing else.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TORCH = "2.10.0"
TORCHVISION = "0.25.0"

CPU_FLAVOR = "cpu"
CUDA_FLAVOR = "cuda128"
CUDA_WHEEL_TAG = "cu128"
CUDA_VERSION_LABEL = "12.8"

PYTORCH_INDEX_BASE = "https://download.pytorch.org/whl"
CPU_INDEX_URL = f"{PYTORCH_INDEX_BASE}/cpu"
CUDA_INDEX_URL = f"{PYTORCH_INDEX_BASE}/{CUDA_WHEEL_TAG}"

SUPPORTED_FLAVORS = frozenset({CPU_FLAVOR, CUDA_FLAVOR})


def flavor_for_wheel_tag(wheel_tag: str) -> str:
    """Map a PyTorch wheel index tag (``cpu`` or ``cu<digits>``) to a flavor."""
    if wheel_tag == "cpu":
        return CPU_FLAVOR
    if not (wheel_tag.startswith("cu") and wheel_tag[2:].isdigit()):
        raise ValueError(f"not a PyTorch wheel tag: {wheel_tag!r}")
    return "cuda" + wheel_tag[2:]


def cuda_version_label(flavor: str) -> str:
    """Map ``cuda<major><minor>`` (for example ``cuda128``) to ``12.8``."""
    digits = flavor[len("cuda"):]
    if not flavor.startswith("cuda") or not digits.isdigit() or len(digits) < 3:
        raise ValueError(f"not a CUDA flavor: {flavor!r}")
    return f"{digits[:-1]}.{digits[-1]}"


def matched_torchvision_minor(torch_version: str) -> str:
    """Return the torchvision ``0.<minor>`` release line paired with torch 2.x.

    PyTorch releases torch ``2.N`` together with torchvision ``0.(15 + N)``
    (2.0/0.15 ... 2.6/0.21 ... 2.10/0.25).
    """
    major, minor = (int(part) for part in torch_version.split(".")[:2])
    if major != 2:
        raise ValueError(f"unsupported torch major version: {torch_version!r}")
    return f"0.{15 + minor}"


def tracked_files(*pathspecs: str, root: Path = REPO_ROOT) -> list[Path] | None:
    """Return the git-tracked files under ``pathspecs`` (all files if none).

    Returns ``None`` when git or the repository metadata is unavailable (for
    example in an exported source tree) so callers can fall back to walking
    the filesystem. Untracked files are never returned.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", *pathspecs],
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return [root / name for name in names if name and (root / name).is_file()]
