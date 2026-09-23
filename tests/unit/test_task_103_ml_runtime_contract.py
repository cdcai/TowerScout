"""TASK-103 ML runtime contract: flavor set, exact pins and index URLs (N1-N3).

Every place that writes the torch/torchvision pair, the PyTorch flavor or the
PyTorch wheel index URL must agree with ``ml_runtime_contract``. These are
static checks, so they run on every platform (the PowerShell behavior itself is
covered by the Windows-only launcher and packaging tests).
"""

from __future__ import annotations

import fnmatch
import re

import pytest
import yaml

import release_manifest_contract
from ml_runtime_contract import (
    CPU_FLAVOR,
    CPU_INDEX_URL,
    CUDA_FLAVOR,
    CUDA_INDEX_URL,
    CUDA_VERSION_LABEL,
    CUDA_WHEEL_TAG,
    PYTORCH_INDEX_BASE,
    REPO_ROOT,
    SUPPORTED_FLAVORS,
    TORCH,
    TORCHVISION,
    cuda_version_label,
    flavor_for_wheel_tag,
    matched_torchvision_minor,
    tracked_files,
)

REQUIREMENTS = REPO_ROOT / "webapp" / "requirements.txt"
DOCKERFILE = REPO_ROOT / "Dockerfile"
COMPOSE_BUILD = REPO_ROOT / "compose.build.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "container-publish.yml"
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"
HARNESS = REPO_ROOT / "scripts" / "task098-qualify-ml.ps1"

# A superseded flavor, built dynamically so this file never trips the stale
# CUDA reference scan in test_task_098_slice_dg.py.
STALE_CUDA_FLAVORS = ("cuda" + "121", "cuda" + "126")


def _read(path):
    return path.read_text(encoding="utf-8")


def _single(pattern, text, flags=re.MULTILINE):
    matches = re.findall(pattern, text, flags)
    assert len(matches) == 1, f"expected exactly one match for {pattern!r}, got {matches!r}"
    return matches[0]


def _workflow():
    return yaml.safe_load(_read(WORKFLOW))


def _workflow_dispatch_inputs(workflow):
    # PyYAML (YAML 1.1) loads the bare key ``on`` as boolean True.
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict), "container-publish.yml has no trigger map"
    return triggers["workflow_dispatch"]["inputs"]


def _workflow_build_script(workflow):
    steps = workflow["jobs"]["publish"]["steps"]
    scripts = [step["run"] for step in steps if step.get("id") == "build"]
    assert len(scripts) == 1
    return scripts[0]


def _case_body(script, subject):
    return _single(
        r'case "\$' + re.escape(subject) + r'" in\n(.*?)\n\s*esac',
        script,
        flags=re.DOTALL,
    )


def _workflow_flavor_index_urls(script):
    body = _case_body(script, "pytorch_flavor")
    branches = dict(
        re.findall(
            r'^\s*([A-Za-z0-9_]+)\)\s*\n\s*pytorch_index_url="([^"]+)"',
            body,
            flags=re.MULTILINE,
        )
    )
    assert re.search(r"^\s*\*\)\s*\n[^;]*exit 1", body, flags=re.MULTILINE), (
        "unsupported flavors must fail the publish job"
    )
    return branches


def _workflow_tag_guard(script):
    body = _case_body(script, "tag")
    return re.findall(r"^\s*([^\s()]+)\)\s*$", body, flags=re.MULTILINE)[0]


def _requirement_pins(text):
    pins = {}
    for line in text.splitlines():
        match = re.match(
            r"^\s*(torch|torchvision)\s*(===|==|~=|!=|<=|>=|<|>)\s*([^\s;#]+)",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            name = match.group(1).lower()
            assert name not in pins, f"duplicate {name} requirement"
            pins[name] = (match.group(2), match.group(3))
    return pins


def _compose_build_args():
    compose = yaml.safe_load(_read(COMPOSE_BUILD))
    return compose["services"]["towerscout"]["build"]["args"]


def _compose_default(args, name):
    return _single(r"^\$\{" + re.escape(name) + r":-([^}]+)\}$", str(args[name]))


def _harness_default(name):
    return _single(r"\[string\]\s*\$" + re.escape(name) + r'\s*=\s*"([^"]*)"', _read(HARNESS))


# --------------------------------------------------------------------------
# Contract module self-consistency
# --------------------------------------------------------------------------


def test_contract_constants_are_self_consistent():
    assert flavor_for_wheel_tag(CUDA_WHEEL_TAG) == CUDA_FLAVOR
    assert flavor_for_wheel_tag("cpu") == CPU_FLAVOR
    assert cuda_version_label(CUDA_FLAVOR) == CUDA_VERSION_LABEL
    assert CUDA_INDEX_URL == f"{PYTORCH_INDEX_BASE}/{CUDA_WHEEL_TAG}"
    assert CPU_INDEX_URL == f"{PYTORCH_INDEX_BASE}/cpu"
    assert SUPPORTED_FLAVORS == {CPU_FLAVOR, CUDA_FLAVOR}
    assert not set(STALE_CUDA_FLAVORS) & SUPPORTED_FLAVORS


# --------------------------------------------------------------------------
# N1: the flavor set is exactly {cpu, cuda128} everywhere
# --------------------------------------------------------------------------


def test_n1_workflow_flavor_options_and_branches_match_contract():
    workflow = _workflow()
    flavor_input = _workflow_dispatch_inputs(workflow)["pytorch_flavor"]
    script = _workflow_build_script(workflow)

    assert flavor_input["type"] == "choice"
    assert flavor_input["default"] == CPU_FLAVOR
    assert len(flavor_input["options"]) == len(set(flavor_input["options"]))
    assert set(flavor_input["options"]) == SUPPORTED_FLAVORS
    assert set(_workflow_flavor_index_urls(script)) == SUPPORTED_FLAVORS


def test_n1_workflow_tag_guard_is_generic_and_fails_closed_on_other_cuda_suffixes():
    guard = _workflow_tag_guard(_workflow_build_script(_workflow()))
    assert guard == "*-cpu|*-cuda[0-9]*"

    def guarded(tag):
        return any(fnmatch.fnmatchcase(tag, pattern) for pattern in guard.split("|"))

    # Supported suffixes enter the "already suffixed" branch, which then
    # requires the suffix to equal the selected flavor.
    for flavor in SUPPORTED_FLAVORS:
        assert guarded(f"v1.2.3-{flavor}")
    # A superseded CUDA suffix is guarded too, so it is rejected as a flavor
    # mismatch instead of being re-suffixed into v1.2.3-<old>-cuda128.
    for stale in STALE_CUDA_FLAVORS:
        assert guarded(f"v1.2.3-{stale}")
    assert not guarded("v1.2.3")
    assert not guarded("v1.2.3-rc1")


def test_n1_package_release_allow_list_matches_contract():
    script = _read(PACKAGE_SCRIPT)
    allow_list = _single(r"^\$supportedPytorchFlavors\s*=\s*@\(([^)]*)\)", script)

    assert set(re.findall(r'"([^"]+)"', allow_list)) == SUPPORTED_FLAVORS
    assert "$PytorchFlavor -notin $supportedPytorchFlavors" in script
    # Inference and the asset-bundle suffix strip are generic; the allow-list
    # is the only place that names the concrete CUDA flavor.
    assert '-match "[-:](cpu|cuda\\d+)$"' in script
    assert "-match '^(?<base>.+)-(?:cpu|cuda\\d+)$'" in script
    assert set(re.findall(r"cuda\d+", script)) == {CUDA_FLAVOR}


def test_n1_release_manifest_contract_matches_contract():
    assert release_manifest_contract.SUPPORTED_PYTORCH_FLAVORS == SUPPORTED_FLAVORS


def test_n1_launcher_flavors_and_guidance_match_contract():
    library = _read(COMPOSE_LIB)
    assigned = set(
        re.findall(r'\$env:TOWERSCOUT_PYTORCH_FLAVOR\s*=\s*"([^"]+)"', library)
    )

    assert assigned == SUPPORTED_FLAVORS
    assert f"Use the CUDA {CUDA_VERSION_LABEL} package" in library
    assert set(re.findall(r"CUDA (\d+\.\d+) package", library)) == {CUDA_VERSION_LABEL}


def test_n1_build_defaults_select_a_supported_flavor():
    assert _single(r"^ARG TOWERSCOUT_PYTORCH_FLAVOR=(\S+)$", _read(DOCKERFILE)) in SUPPORTED_FLAVORS
    assert (
        _compose_default(_compose_build_args(), "TOWERSCOUT_PYTORCH_FLAVOR")
        in SUPPORTED_FLAVORS
    )
    assert _single(r"^TOWERSCOUT_PYTORCH_FLAVOR=(\S+)$", _read(ENV_EXAMPLE)) in SUPPORTED_FLAVORS


def test_n1_harness_default_wheel_tag_derives_the_cuda_flavor():
    harness = _read(HARNESS)
    wheel_tag = _harness_default("CudaWheelTag")
    validate_pattern = _single(
        r"\[ValidatePattern\('([^']+)'\)\]\s*\n\s*\[string\]\s*\$CudaWheelTag", harness
    )

    assert re.fullmatch(validate_pattern, wheel_tag, flags=re.IGNORECASE)
    assert '"cuda" + $CudaWheelTag.Substring(2)' in harness
    assert flavor_for_wheel_tag(wheel_tag) == CUDA_FLAVOR


# --------------------------------------------------------------------------
# N2: exact == pins agree, and torchvision is the matched release line
# --------------------------------------------------------------------------


def test_n2_contract_pair_is_a_matched_release_pair():
    assert TORCHVISION.rsplit(".", 1)[0] == matched_torchvision_minor(TORCH)


@pytest.mark.parametrize(
    "torch_version,torchvision_minor",
    [("2.6.0", "0.21"), ("2.9.1", "0.24"), ("2.10.0", "0.25"), ("2.11.0", "0.26")],
)
def test_n2_torchvision_pairing_rule(torch_version, torchvision_minor):
    assert matched_torchvision_minor(torch_version) == torchvision_minor


def test_n2_requirements_pin_the_pair_exactly():
    pins = _requirement_pins(_read(REQUIREMENTS))

    assert pins == {"torch": ("==", TORCH), "torchvision": ("==", TORCHVISION)}


def test_n2_dockerfile_strips_every_torch_requirement_before_the_runtime_install():
    dockerfile = _read(DOCKERFILE)
    strip_pattern = _single(r"grep -Ev '([^']+)' webapp/requirements\.txt", dockerfile)
    remaining = [
        line
        for line in _read(REQUIREMENTS).splitlines()
        if not re.search(strip_pattern, line)
    ]

    assert '"torch==${TOWERSCOUT_TORCH_VERSION}"' in dockerfile
    assert '"torchvision==${TOWERSCOUT_TORCHVISION_VERSION}"' in dockerfile
    assert _requirement_pins("\n".join(remaining)) == {}


def test_n2_build_and_release_pins_agree_everywhere():
    dockerfile = _read(DOCKERFILE)
    env_example = _read(ENV_EXAMPLE)
    workflow_script = _workflow_build_script(_workflow())
    compose_args = _compose_build_args()

    torch_pins = {
        "Dockerfile": _single(r"^ARG TOWERSCOUT_TORCH_VERSION=(\S+)$", dockerfile),
        "compose.build.yaml": _compose_default(compose_args, "TOWERSCOUT_TORCH_VERSION"),
        ".env.example": _single(r"^TOWERSCOUT_TORCH_VERSION=(\S+)$", env_example),
        "container-publish.yml": _single(
            r'--build-arg TOWERSCOUT_TORCH_VERSION="([^"]+)"', workflow_script
        ),
        "task098-qualify-ml.ps1": _harness_default("TorchVersion"),
    }
    torchvision_pins = {
        "Dockerfile": _single(r"^ARG TOWERSCOUT_TORCHVISION_VERSION=(\S+)$", dockerfile),
        "compose.build.yaml": _compose_default(
            compose_args, "TOWERSCOUT_TORCHVISION_VERSION"
        ),
        ".env.example": _single(r"^TOWERSCOUT_TORCHVISION_VERSION=(\S+)$", env_example),
        "container-publish.yml": _single(
            r'--build-arg TOWERSCOUT_TORCHVISION_VERSION="([^"]+)"', workflow_script
        ),
        "task098-qualify-ml.ps1": _harness_default("TorchvisionVersion"),
    }

    assert torch_pins == {source: TORCH for source in torch_pins}
    assert torchvision_pins == {source: TORCHVISION for source in torchvision_pins}


# --------------------------------------------------------------------------
# N3: the CUDA (and CPU) wheel index URLs agree everywhere they are written
# --------------------------------------------------------------------------


def test_n3_workflow_launcher_and_harness_use_the_contract_index_urls():
    workflow_urls = _workflow_flavor_index_urls(_workflow_build_script(_workflow()))
    library = _read(COMPOSE_LIB)
    harness = _read(HARNESS)

    assert workflow_urls == {CPU_FLAVOR: CPU_INDEX_URL, CUDA_FLAVOR: CUDA_INDEX_URL}
    assert (
        _single(r'^\$script:TowerScoutCudaPytorchIndexUrl\s*=\s*"([^"]+)"', library)
        == CUDA_INDEX_URL
    )
    assert (
        _single(r'^\$script:TowerScoutCpuPytorchIndexUrl\s*=\s*"([^"]+)"', library)
        == CPU_INDEX_URL
    )
    assert f'$indexUrl = "{PYTORCH_INDEX_BASE}/$wheelTag"' in harness
    assert f"{PYTORCH_INDEX_BASE}/{_harness_default('CudaWheelTag')}" == CUDA_INDEX_URL


def test_n3_cpu_index_defaults_agree():
    assert _single(r"^ARG PYTORCH_INDEX_URL=(\S+)$", _read(DOCKERFILE)) == CPU_INDEX_URL
    assert _compose_default(_compose_build_args(), "PYTORCH_INDEX_URL") == CPU_INDEX_URL
    assert _single(r"^PYTORCH_INDEX_URL=(\S+)$", _read(ENV_EXAMPLE)) == CPU_INDEX_URL


def test_n3_every_tracked_pytorch_cuda_index_url_is_the_contract_url():
    candidates = tracked_files()
    if candidates is None:
        pytest.skip("git metadata unavailable; the explicit N3 checks still apply")
    url_pattern = re.compile(re.escape(PYTORCH_INDEX_BASE) + r"/(cu\d+)\b")
    offenders = []
    for path in candidates:
        relative = path.relative_to(REPO_ROOT).as_posix()
        # Governance and legacy material are out of the runtime contract.
        if relative.startswith(".agent_work/") or "legacy" in relative.split("/"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for match in url_pattern.finditer(text):
            if match.group(1) != CUDA_WHEEL_TAG:
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{relative}:{line}: {match.group(0)}")

    assert offenders == []
