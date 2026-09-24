"""Task-098 Slice D/G dependency and model-trust contracts."""

import fnmatch
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import textwrap
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import towerscout
import ts_assets
import ts_en
import ts_yolov5
from ml_runtime_contract import TORCH as TORCH_VERSION
from ml_runtime_contract import TORCHVISION as TORCHVISION_VERSION
from ml_runtime_contract import tracked_files
from ts_assets import AssetManifestError
from towerscout import app

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_UPLOAD_KEY = "task098-model-upload-key-1234567890"
RUNTIME_CONTRACT = REPO_ROOT / "docs" / "support" / "oci-runtime-contract.md"
ASSET_CONTRACT = (
    REPO_ROOT / "docs" / "release" / "release-asset-bundle-contract.md"
)


def _scratch_root() -> Path:
    root = Path.cwd() / ".agent_work" / "pytest-temp" / f"task098-dg-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    return root


def _write_manifest(root: Path, model_path: Path, content: bytes) -> Path:
    relative_path = model_path.relative_to(root).as_posix()
    manifest_path = root / "asset_manifest.v1.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "manifest_version": "task098-test",
                "assets": [
                    {
                        "id": "trusted-test-model",
                        "kind": "model",
                        "path": relative_path,
                        "required": True,
                        "bytes": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


def test_selected_torch_pair_is_pinned_consistently():
    requirements = (REPO_ROOT / "webapp" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    compose_build = (REPO_ROOT / "compose.build.yaml").read_text(encoding="utf-8")

    assert f"torch=={TORCH_VERSION}" in requirements
    assert f"torchvision=={TORCHVISION_VERSION}" in requirements
    assert f"ARG TOWERSCOUT_TORCH_VERSION={TORCH_VERSION}" in dockerfile
    assert f"ARG TOWERSCOUT_TORCHVISION_VERSION={TORCHVISION_VERSION}" in dockerfile
    assert f"TOWERSCOUT_TORCH_VERSION:-{TORCH_VERSION}" in compose_build
    assert f"TOWERSCOUT_TORCHVISION_VERSION:-{TORCHVISION_VERSION}" in compose_build


def test_cross_device_harness_is_commit_pinned_and_isolated():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    harness = (REPO_ROOT / "scripts" / "task098-qualify-ml.ps1").read_text(
        encoding="utf-8"
    )
    probe = (REPO_ROOT / "scripts" / "task098_ml_qualification.py").read_text(
        encoding="utf-8"
    )

    assert "status --porcelain --untracked-files=no" in harness
    assert "--pull" in harness
    assert "--no-cache" in harness
    assert "--rm" in harness
    assert "--read-only" in harness
    assert "--gpus" in harness
    assert "BuildCaBundlePath" in harness
    assert "id=towerscout_build_ca,src=$resolvedBuildCa" in harness
    assert (
        "--mount=type=secret,id=towerscout_build_ca,required=false" in dockerfile
    )
    assert "PIP_CERT=/run/secrets/towerscout_build_ca" in dockerfile
    assert "--trusted-host" not in dockerfile
    assert "source_commit" in probe
    assert "output_matches_declared_tolerance" in probe
    assert "selected_devices_match_request" in probe


@pytest.mark.skipif(os.name != "nt", reason="PowerShell harness is Windows-only")
def test_cross_device_harness_rejects_build_ca_inside_context(tmp_path):
    powershell = shutil.which("powershell.exe") or shutil.which("pwsh")
    if powershell is None:
        pytest.skip("PowerShell executable not found")

    sandbox = tmp_path / "TowerScout qualification sandbox"
    scripts = sandbox / "scripts"
    webapp = sandbox / "webapp"
    fake_bin = tmp_path / "fake-bin"
    scripts.mkdir(parents=True)
    webapp.mkdir()
    fake_bin.mkdir()
    harness = scripts / "task098-qualify-ml.ps1"
    shutil.copy2(REPO_ROOT / "scripts" / harness.name, harness)
    ca_bundle = webapp / "managed-build-ca.pem"
    ca_bundle.write_text("private managed CA", encoding="ascii")
    build_marker = tmp_path / "docker-build-called.txt"

    (fake_bin / "git.cmd").write_text(
        textwrap.dedent(
            """\
            @echo off
            if "%3"=="status" exit /b 0
            if "%3"=="rev-parse" (
              echo 0123456789abcdef0123456789abcdef01234567
              exit /b 0
            )
            exit /b 2
            """
        ),
        encoding="ascii",
    )
    (fake_bin / "docker.cmd").write_text(
        textwrap.dedent(
            f"""\
            @echo off
            if "%1"=="info" (
              echo 29.7.2
              exit /b 0
            )
            if "%1"=="build" (
              echo called>"{build_marker}"
              exit /b 0
            )
            exit /b 0
            """
        ),
        encoding="ascii",
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(harness),
            "-BuildCaBundlePath",
            str(ca_bundle),
        ],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "outside the Docker build context" in result.stdout + result.stderr
    assert not build_marker.exists()


def test_release_model_hash_is_verified_by_default(monkeypatch):
    root = _scratch_root()
    try:
        content = b"trusted-model-content"
        model_path = root / "model_params" / "yolov5" / "newest.pt"
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(content)
        manifest_path = _write_manifest(root, model_path, content)
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        result = ts_assets.verify_trusted_model(model_path)
        status = ts_assets.build_asset_status()

        assert result["source"] == "release_manifest"
        assert result["sha256"] == hashlib.sha256(content).hexdigest().upper()
        assert status["verify_hashes"] is False
        assert status["verify_model_hashes"] is True
        assert status["assets"][0]["sha256"] == result["sha256"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_release_model_hash_mismatch_is_rejected(monkeypatch):
    root = _scratch_root()
    try:
        expected = b"expected-model-content"
        model_path = root / "model_params" / "yolov5" / "newest.pt"
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(expected)
        manifest_path = _write_manifest(root, model_path, expected)
        model_path.write_bytes(b"tampered-model-content")
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        with pytest.raises(AssetManifestError, match="verification"):
            ts_assets.verify_trusted_model(model_path)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_yolo_verifies_model_before_deserializing(monkeypatch):
    order = []
    fake_model = Mock()
    fake_model.cpu.return_value = None
    monkeypatch.setattr(ts_yolov5.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(ts_yolov5, "_validate_runtime_dependencies", lambda: None)
    monkeypatch.setattr(
        ts_yolov5,
        "verify_trusted_model",
        lambda _path: order.append("verify"),
    )
    monkeypatch.setattr(
        ts_yolov5,
        "_load_local_yolov5_model",
        lambda _path: order.append("load") or fake_model,
    )
    monkeypatch.setattr(
        ts_yolov5,
        "select_model_device",
        lambda *_args, **_kwargs: Mock(
            selected_device="cpu",
            requested_policy="cpu",
            fallback_reason=None,
        ),
    )

    ts_yolov5.YOLOv5_Detector("trusted.pt")

    assert order == ["verify", "load"]


def test_efficientnet_verifies_model_before_torch_load(monkeypatch):
    root = _scratch_root()
    try:
        model_path = root / "b5_unweighted_best.pt"
        model_path.write_bytes(b"trusted")
        order = []
        fake_model = Mock()
        fake_model.to.return_value = fake_model
        monkeypatch.setattr(ts_en, "get_en_model_dir", lambda: root)
        monkeypatch.setattr(
            ts_en,
            "verify_trusted_model",
            lambda _path: order.append("verify"),
        )
        monkeypatch.setattr(
            ts_en.EfficientNet,
            "from_name",
            lambda *_args, **_kwargs: fake_model,
        )
        monkeypatch.setattr(
            ts_en.torch,
            "load",
            lambda *_args, **_kwargs: order.append("load") or {},
        )
        monkeypatch.setattr(
            ts_en,
            "select_model_device",
            lambda *_args, **_kwargs: Mock(
                selected_device="cpu",
                requested_policy="cpu",
                fallback_reason=None,
            ),
        )

        ts_en.EN_Classifier()

        assert order[:2] == ["verify", "load"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "task098-secret"
    return app.test_client()


def test_model_upload_override_rejects_missing_key_from_container_peer(
    client, monkeypatch
):
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
    monkeypatch.setenv("TOWERSCOUT_MODEL_UPLOAD_KEY", MODEL_UPLOAD_KEY)

    response = client.post(
        "/uploadmodel",
        data={"model": (io.BytesIO(b"model"), "custom.pt")},
        content_type="multipart/form-data",
        environ_base={
            "REMOTE_ADDR": "192.0.2.10",
            "HTTP_X_FORWARDED_FOR": "127.0.0.1",
        },
    )

    assert response.status_code == 403
    assert "authorization" in response.get_json()["error"].lower()


def test_model_upload_override_fails_closed_without_configured_key(client, monkeypatch):
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
    monkeypatch.delenv("TOWERSCOUT_MODEL_UPLOAD_KEY", raising=False)

    response = client.post(
        "/uploadmodel",
        data={"model": (io.BytesIO(b"model"), "custom.pt")},
        content_type="multipart/form-data",
        headers={"X-TowerScout-Model-Upload-Key": MODEL_UPLOAD_KEY},
    )

    assert response.status_code == 503
    error = response.get_json()["error"].lower()
    assert "no valid model upload key" in error
    assert "configured" in error


def test_model_upload_override_accepts_key_from_container_peer_then_rejects_untrusted_file(
    client, monkeypatch
):
    root = _scratch_root()
    try:
        monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
        monkeypatch.setattr(towerscout, "YOLO_MODEL_DIR", root)
        monkeypatch.setattr(towerscout, "EN_MODEL_DIR", root)
        monkeypatch.setenv("TOWERSCOUT_MODEL_UPLOAD_KEY", MODEL_UPLOAD_KEY)
        monkeypatch.delenv("TOWERSCOUT_TRUSTED_MODEL_SHA256", raising=False)

        with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True):
            response = client.post(
                "/uploadmodel",
                data={"model": (io.BytesIO(b"untrusted"), "custom.pt")},
                content_type="multipart/form-data",
                headers={"X-TowerScout-Model-Upload-Key": MODEL_UPLOAD_KEY},
                environ_base={"REMOTE_ADDR": "172.17.0.1"},
            )

        assert response.status_code == 400
        assert "trust" in response.get_json()["error"].lower()
        assert not (root / "custom.pt").exists()
        assert list(root.glob(".custom.pt.*.pending")) == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_model_upload_container_and_frontend_contracts_require_the_dedicated_key():
    compose = (REPO_ROOT / "compose.yaml").read_text(encoding="utf-8")
    env_template = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    webapp_env_template = (REPO_ROOT / "webapp" / ".env.example").read_text(
        encoding="utf-8"
    )
    template = (
        REPO_ROOT / "webapp" / "templates" / "towerscout.html"
    ).read_text(encoding="utf-8")
    frontend = (
        REPO_ROOT / "webapp" / "js" / "src" / "towerscout.js"
    ).read_text(encoding="utf-8")

    assert "127.0.0.1:${TOWERSCOUT_PORT:-5000}:5000" in compose
    for variable in (
        "TOWERSCOUT_ENABLE_MODEL_UPLOAD",
        "TOWERSCOUT_MODEL_UPLOAD_KEY",
        "TOWERSCOUT_TRUSTED_MODEL_SHA256",
    ):
        assert variable in compose
        assert variable in env_template
        assert variable in webapp_env_template

    assert 'id="model_upload_key"' in template
    assert 'type="password"' in template
    assert 'autocomplete="off"' in template
    assert "X-TowerScout-Model-Upload-Key" in frontend
    assert "installed model \" + model" not in frontend


# Superseded CUDA names are built dynamically so the literal tokens stay out
# of this file (it is also exempt from its own scan).
_OLD_CUDA_TAG = "cu" + "126"

STALE_CUDA_PATTERN = re.compile(
    r"\b(?:cuda(?:\s+|[-_])?12\.[16]|cuda12[16]|cu12[16])\b",
    flags=re.IGNORECASE,
)
# Explicit file roots are always scanned, whatever their suffix (Dockerfile has
# none); directory roots are scanned for the text suffixes below.
STALE_SCAN_ROOTS = (
    "Dockerfile",
    "compose.yaml",
    "compose.build.yaml",
    "compose.gpu.yaml",
    "compose.gpu.podman.yaml",
    ".env.example",
    "README.md",
    "HANDOFF.md",
    "webapp",
    "scripts",
    "docs",
    "tests",
    ".github",
    ".agents/skills",
)
STALE_SCAN_TEXT_SUFFIXES = {
    ".bat",
    ".cmd",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}
# Whole files that legitimately name the superseded baseline flavor because
# they measure or compare against it (the TASK-103 pilot tooling). Keys are
# repo-relative POSIX globs; values are the justification.
STALE_CUDA_FILE_ALLOWLIST = {
    "scripts/task103_compare.py": (
        "TASK-103 comparator: judges candidate stage C against the stage A/B "
        "baseline flavor."
    ),
    "scripts/task103_pilot_probe.py": (
        "TASK-103 in-image probe: reports whichever wheel tag and arch list "
        "the baseline or candidate image carries."
    ),
    "tests/unit/test_task103_*.py": (
        "TASK-103 pilot tooling tests: fixtures model the stage A/B baseline "
        "arch list, wheel tag and flavor."
    ),
}
# Individual lines that keep a superseded CUDA name on purpose. Maps a
# repo-relative path to {substring of the matched line: justification}; every
# entry must still match something, so stale entries are pruned.
STALE_CUDA_LINE_ALLOWLIST = {
    "scripts/task103_gates.v1.json": {
        f'"{_OLD_CUDA_TAG}": "12.6"': (
            "Declared (frozen) TASK-103 gates map the stage A/B baseline wheel "
            "tag to its CUDA build."
        ),
    },
    "scripts/task103_gates.v2.json": {
        f'"{_OLD_CUDA_TAG}": "12.6"': (
            "Declared (frozen) TASK-103 gates v2 map the stage A/B baseline "
            "wheel tag to its CUDA build."
        ),
    },
    "scripts/task103_gates.v3.json": {
        f'"{_OLD_CUDA_TAG}": "12.6"': (
            "Declared TASK-103 gates v3 map the stage A/B baseline wheel tag "
            "to its CUDA build."
        ),
    },
}


def _stale_scan_candidates():
    """Yield (relative POSIX path, path) for every file the stale scan reads.

    Uses ``git ls-files`` so untracked drafts never count; falls back to a
    filesystem walk only when git metadata is unavailable.
    """
    file_roots = {root for root in STALE_SCAN_ROOTS if (REPO_ROOT / root).is_file()}
    paths = tracked_files(*STALE_SCAN_ROOTS, root=REPO_ROOT)
    if paths is None:
        paths = []
        for root in STALE_SCAN_ROOTS:
            root_path = REPO_ROOT / root
            if root_path.is_file():
                paths.append(root_path)
            elif root_path.is_dir():
                paths.extend(path for path in root_path.rglob("*") if path.is_file())
    this_file = Path(__file__).resolve().relative_to(REPO_ROOT).as_posix()
    for path in sorted(set(paths)):
        relative = path.relative_to(REPO_ROOT).as_posix()
        if (
            relative == this_file
            or "legacy" in {part.lower() for part in relative.split("/")}
            or (
                relative not in file_roots
                and path.suffix.lower() not in STALE_SCAN_TEXT_SUFFIXES
            )
        ):
            continue
        yield relative, path


@pytest.mark.parametrize(
    "text",
    [
        "CUDA 12" + ".6",
        "CUDA\n12" + ".1 Application Package",
        "cuda-12" + ".6",
        "cuda_12" + ".1",
        "cuda12" + ".6",
        "cuda" + "126",
        "CUDA" + "121",
        "cu" + "126",
        "whl/cu" + "121",
    ],
)
def test_stale_cuda_pattern_matches_superseded_spellings(text):
    assert STALE_CUDA_PATTERN.search(text)


@pytest.mark.parametrize(
    "text",
    [
        "CUDA 12.8",
        "cuda128",
        "cu128",
        "whl/cu128",
        "12" + ".6 alone",
        "cu" + "1260",
        "sm_126",
    ],
)
def test_stale_cuda_pattern_ignores_current_and_unrelated_tokens(text):
    assert not STALE_CUDA_PATTERN.search(text)


def test_current_contracts_have_no_stale_cuda_reference():
    assert all(STALE_CUDA_FILE_ALLOWLIST.values())
    assert all(
        justification
        for entries in STALE_CUDA_LINE_ALLOWLIST.values()
        for justification in entries.values()
    )
    stale_references = []
    used_line_entries = set()

    for relative, path in _stale_scan_candidates():
        if any(
            fnmatch.fnmatchcase(relative, pattern)
            for pattern in STALE_CUDA_FILE_ALLOWLIST
        ):
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        line_entries = STALE_CUDA_LINE_ALLOWLIST.get(relative, {})
        for match in STALE_CUDA_PATTERN.finditer(content):
            line_start = content.rfind("\n", 0, match.start()) + 1
            line_end = content.find("\n", match.end())
            line_end = len(content) if line_end == -1 else line_end
            matched_lines = content[line_start:line_end]
            allowed = [
                substring for substring in line_entries if substring in matched_lines
            ]
            if allowed:
                used_line_entries.update((relative, substring) for substring in allowed)
                continue
            line_number = content.count("\n", 0, match.start()) + 1
            stale_references.append(
                f"{relative}:{line_number}: {match.group(0)!r}"
            )

    unused_line_entries = [
        f"{relative}: {substring!r}"
        for relative, entries in STALE_CUDA_LINE_ALLOWLIST.items()
        for substring in entries
        if (relative, substring) not in used_line_entries
    ]

    assert stale_references == [], "Stale CUDA references:\n" + "\n".join(
        stale_references
    )
    assert unused_line_entries == [], "Unused line allowlist entries:\n" + "\n".join(
        unused_line_entries
    )


def test_runtime_docs_distinguish_always_on_model_hashes_from_full_asset_hashes():
    runtime_contract = RUNTIME_CONTRACT.read_text(encoding="utf-8")
    asset_contract = ASSET_CONTRACT.read_text(encoding="utf-8")
    normalized_runtime_contract = " ".join(runtime_contract.split())
    normalized_asset_contract = " ".join(asset_contract.split())

    assert (
        "model assets are always SHA-256 verified"
        in normalized_runtime_contract
    )
    assert (
        "Model hash verification remains enabled."
        in normalized_asset_contract
    )
    assert (
        "model loading rejects it before deserialization"
        in normalized_asset_contract
    )
