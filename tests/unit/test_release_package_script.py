import shutil
import subprocess
import uuid
import os
import json
import hashlib
import posixpath
import re
import zipfile
from urllib.parse import unquote, urlsplit
from pathlib import Path

import pytest

from release_manifest_contract import (
    REQUIRED_COMPLIANCE_FILES,
    assert_manifest_schema,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"
DEFERRED_HELPER_FILES = (
    "scripts/host-helper.cmd",
    "scripts/host-helper.ps1",
    "scripts/host-helper-worker.ps1",
    "scripts/lib/TowerScoutHostHelper.ps1",
)

pytestmark = pytest.mark.skipif(
    os.name != "nt",
    reason="package-release.ps1 is a Windows release helper validated on Windows",
)


def _run_package_release(*args):
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT),
            *args,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_package_release_requires_digest_by_default():
    result = _run_package_release(
        "-Version",
        f"pytest-no-digest-{uuid.uuid4().hex}",
        "-OutputDir",
        ".agent_work\\pytest-temp\\package-release-no-digest",
        "-Image",
        "ghcr.io/example/towerscout",
        "-NoZip",
        "-Force",
    )

    assert result.returncode != 0
    assert "Release packaging requires -ImageDigest" in (result.stderr + result.stdout)


def test_package_release_rejects_dirty_source_by_default():
    package_id = f"pytest-dirty-{uuid.uuid4().hex}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    digest = "sha256:" + ("2" * 64)
    dirty_marker = REPO_ROOT / "tests" / "unit" / f"dirty-marker-{uuid.uuid4().hex}.txt"
    try:
        dirty_marker.write_text("dirty tree marker", encoding="utf-8")
        result = _run_package_release(
            "-Version",
            package_id,
            "-OutputDir",
            str(output_dir),
            "-Image",
            "ghcr.io/example/towerscout",
            "-ImageDigest",
            digest,
            "-NoZip",
            "-Force",
        )

        assert result.returncode != 0
        assert "Release packaging requires a clean git working tree" in (
            result.stderr + result.stdout
        )
    finally:
        dirty_marker.unlink(missing_ok=True)
        shutil.rmtree(output_path, ignore_errors=True)


@pytest.mark.parametrize("image_repository", ["ghcr.io/cdcai/towerscout", "ghcr.io/example/towerscout"])
def test_package_release_stages_digest_pinned_image(image_repository):
    package_id = f"pytest-digest-{uuid.uuid4().hex}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    digest = "sha256:" + ("1" * 64)
    asset_bundle_sha256 = "4" * 64
    dirty_marker = REPO_ROOT / "tests" / "unit" / f"dirty-marker-{uuid.uuid4().hex}.txt"
    try:
        dirty_marker.write_text("dirty tree marker", encoding="utf-8")
        result = _run_package_release(
            "-Version",
            package_id,
            "-OutputDir",
            str(output_dir),
            "-Image",
            f"{image_repository}:pytest-digest-cuda128",
            "-ImageDigest",
            digest,
            "-AssetBundleSha256",
            asset_bundle_sha256,
            "-PytorchFlavor",
            "cuda128",
            "-AllowDirtySource",
            "-NoZip",
            "-Force",
        )

        assert result.returncode == 0, result.stderr + result.stdout
        stage_path = output_path / f"towerscout-{package_id}"
        env_example = (stage_path / ".env.example").read_text(encoding="utf-8")
        image_txt = (stage_path / "IMAGE.txt").read_text(encoding="utf-8")
        asset_readme = (stage_path / "assets" / "README.txt").read_text(encoding="utf-8")
        release_manifest = json.loads(
            (stage_path / "release-manifest.v1.json").read_text(encoding="utf-8")
        )
        assert_manifest_schema(release_manifest)
        assert f"TOWERSCOUT_IMAGE={image_repository}:pytest-digest-cuda128@{digest}" in env_example
        assert f"TOWERSCOUT_IMAGE_DIGEST={digest}" in env_example
        assert "TOWERSCOUT_PYTORCH_FLAVOR=cuda128" in env_example
        assert f"Image: {image_repository}:pytest-digest-cuda128@{digest}" in image_txt
        assert "PyTorch flavor: cuda128" in image_txt
        assert release_manifest["track"] == "agpl-yolo"
        assert release_manifest["image_digest"] == digest
        assert release_manifest["pytorch_flavor"] == "cuda128"
        assert release_manifest["release_artifacts"]["image_digest"] == digest
        assert release_manifest["release_artifacts"]["pytorch_flavor"] == "cuda128"
        assert release_manifest["release_artifacts"]["control_zip"] == ""
        assert release_manifest["release_artifacts"]["control_zip_sha256"] == ""
        assert release_manifest["release_artifacts"]["control_zip_sha256_sidecar"] == ""
        assert "No control ZIP was generated" in release_manifest["release_artifacts"]["control_zip_sha256_reason"]
        assert release_manifest["release_artifacts"]["asset_bundle"] == (
            f"towerscout-{package_id}-assets-towerscout-v1-assets-2026-05-05.zip"
        )
        assert release_manifest["release_artifacts"]["asset_bundle_release_version"] == package_id
        assert release_manifest["release_artifacts"]["asset_bundle_sha256"] == asset_bundle_sha256
        assert release_manifest["release_artifacts"]["asset_bundle_sha256_sidecar"] == (
            f"towerscout-{package_id}-assets-towerscout-v1-assets-2026-05-05.zip.sha256"
        )
        assert release_manifest["release_artifacts"]["asset_bundle_sha256_reason"] == ""
        assert release_manifest["release_artifacts"]["package_contents_sha256"] == "SHA256SUMS.txt"
        assert REQUIRED_COMPLIANCE_FILES.issubset(
            set(release_manifest["compliance_files"])
        )
        assert release_manifest["corresponding_source"]["source_ref"]
        # This fixture explicitly packages a dirty tree: its parent commit
        # must not be advertised as the exact source for those package bytes.
        assert release_manifest["corresponding_source"]["source_state"] == "local-validation"
        assert release_manifest["corresponding_source"]["source_url"] == ""
        assert release_manifest["corresponding_source"]["archive_url"] == ""
        assert "uncommitted changes" in (stage_path / "SOURCE.txt").read_text()
        assert (
            release_manifest["runtime_components"]["yolo"]["license"]
            == "AGPL-3.0"
        )
        assert release_manifest["sbom"]["reference"] == "SBOM.txt"
        assert "scripts\\import-assets.cmd -Source assets\n" in asset_readme
        assert (
            "scripts\\import-assets.cmd -Source assets -VerifyHashes" in asset_readme
        )
        assert "YOLO-derived/AGPL-governed" in asset_readme
        assert "bootstrap.cmd -AssetZip <path-to-asset-zip>" in asset_readme
        assert (stage_path / "compose.gpu.yaml").is_file()
        assert (stage_path / "compose.gpu.podman.yaml").is_file()
        assert (stage_path / "scripts" / "enable-podman-gpu.ps1").is_file()
        assert (stage_path / "scripts" / "lib" / "TowerScoutPodmanGpu.ps1").is_file()
        assert (stage_path / "scripts" / "lib" / "TowerScoutCertificateStore.ps1").is_file()
        assert (stage_path / "scripts" / "lib" / "TowerScoutHostHelperState.ps1").is_file()
        for excluded in DEFERRED_HELPER_FILES:
            assert not (stage_path / excluded).exists()
        assert (stage_path / "scripts" / "repair-provider-tls.cmd").is_file()
        assert (stage_path / "scripts" / "repair-provider-tls.ps1").is_file()
        for relative_path in [
            "LICENSE",
            "NOTICE",
            "THIRD_PARTY_NOTICES.md",
            "MODEL_LICENSES.md",
            "DATA_LICENSES.md",
            "PROVIDER_TERMS.md",
            "SOURCE.txt",
            "SBOM.txt",
            "release-manifest.v1.json",
        ]:
            assert (stage_path / relative_path).is_file()
        for relative_path in [
            "quick-start.md",
            "quick-start.html",
            "package-guide.md",
            "user-guide.md",
            "user-guide.html",
            "project-overview.md",
            "project-overview.html",
            "local-it-administrator-guide.md",
            "local-it-administrator-guide.html",
            "towerscout-docs.css",
            "v1-rc1-quick-start.md",
            "v1-rc1-quick-start.html",
            "v1-rc1-package-guide.md",
            "towerscout-user-guide.md",
            "towerscout-user-guide.html",
            "support/oci-quick-start.md",
            "support/oci-runtime-contract.md",
            "release/release-asset-bundle-contract.md",
        ]:
            assert (stage_path / "docs" / relative_path).is_file()
        assert not (stage_path / "docs" / "internal").exists()
    finally:
        dirty_marker.unlink(missing_ok=True)
        shutil.rmtree(output_path, ignore_errors=True)


def test_package_release_records_clean_commit_source_urls(tmp_path, monkeypatch):
    """Controlled git responses exercise metadata, not a publication claim."""
    source_ref = "a" * 40
    fake_bin = tmp_path / "source-ref-bin"
    fake_bin.mkdir()
    (fake_bin / "git.cmd").write_text(
        '@echo off\n'
        f'if "%~3"=="rev-parse" echo {source_ref}\n'
        'exit /b 0\n',
        encoding="ascii",
    )
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
    package_id = f"src-{uuid.uuid4().hex[:12]}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    try:
        result = _run_package_release(
            "-Version", package_id, "-OutputDir", str(output_dir),
            "-Image", "ghcr.io/cdcai/towerscout:test-cpu",
            "-ImageDigest", "sha256:" + "1" * 64, "-NoZip",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        stage_path = output_path / f"towerscout-{package_id}"
        source = json.loads((stage_path / "release-manifest.v1.json").read_text())["corresponding_source"]
        assert source["source_state"] == "clean-commit"
        assert source["source_url"] == f"https://github.com/cdcai/TowerScout/tree/{source_ref}"
        assert source["archive_url"] == f"https://github.com/cdcai/TowerScout/archive/{source_ref}.tar.gz"
        notice = (stage_path / "SOURCE.txt").read_text()
        assert source["source_url"] in notice
        assert source["archive_url"] in notice
    finally:
        shutil.rmtree(output_path, ignore_errors=True)


def test_package_release_variants_share_asset_bundle_identity():
    base_id = f"variants-{uuid.uuid4().hex[:12]}"
    output_dir = Path(".agent_work") / "pytest-temp" / base_id
    output_path = REPO_ROOT / output_dir
    asset_bundle_sha256 = "5" * 64
    cpu_digest = "sha256:" + ("6" * 64)
    cuda_digest = "sha256:" + ("7" * 64)
    try:
        for suffix, digest, flavor in [
            ("cpu", cpu_digest, "cpu"),
            ("cuda128", cuda_digest, "cuda128"),
        ]:
            result = _run_package_release(
                "-Version",
                f"{base_id}-{suffix}",
                "-OutputDir",
                str(output_dir),
                "-Image",
                f"ghcr.io/example/towerscout:{base_id}-{suffix}",
                "-ImageDigest",
                digest,
                "-AssetBundleSha256",
                asset_bundle_sha256,
                "-PytorchFlavor",
                flavor,
                "-AllowDirtySource",
                "-NoZip",
                "-Force",
            )
            assert result.returncode == 0, result.stderr + result.stdout

        cpu_manifest = json.loads(
            (
                output_path
                / f"towerscout-{base_id}-cpu"
                / "release-manifest.v1.json"
            ).read_text(encoding="utf-8")
        )
        cuda_manifest = json.loads(
            (
                output_path
                / f"towerscout-{base_id}-cuda128"
                / "release-manifest.v1.json"
            ).read_text(encoding="utf-8")
        )
        assert_manifest_schema(cpu_manifest)
        assert_manifest_schema(cuda_manifest)
        cpu_artifacts = cpu_manifest["release_artifacts"]
        cuda_artifacts = cuda_manifest["release_artifacts"]
        assert cpu_artifacts["asset_bundle_release_version"] == base_id
        assert cuda_artifacts["asset_bundle_release_version"] == base_id
        assert cpu_artifacts["asset_bundle"] == cuda_artifacts["asset_bundle"]
        assert cpu_artifacts["asset_bundle_sha256"] == asset_bundle_sha256
        assert cuda_artifacts["asset_bundle_sha256"] == asset_bundle_sha256
        assert cpu_manifest["pytorch_flavor"] == "cpu"
        assert cuda_manifest["pytorch_flavor"] == "cuda128"
    finally:
        shutil.rmtree(output_path, ignore_errors=True)


def test_package_release_rejects_unknown_pytorch_flavor():
    package_id = f"pytest-flavor-{uuid.uuid4().hex}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    digest = "sha256:" + ("3" * 64)
    try:
        result = _run_package_release(
            "-Version",
            package_id,
            "-OutputDir",
            str(output_dir),
            "-Image",
            "ghcr.io/example/towerscout",
            "-ImageDigest",
            digest,
            "-PytorchFlavor",
            "gpu",
            "-AllowDirtySource",
            "-NoZip",
            "-Force",
        )

        assert result.returncode != 0
        assert "PytorchFlavor must be one of: cpu, cuda128" in (
            result.stderr + result.stdout
        )
    finally:
        shutil.rmtree(output_path, ignore_errors=True)


@pytest.mark.parametrize("flavor", ["cpu", "cuda128"])
def test_control_zip_excludes_deferred_helper_and_preserves_launch_stop(
    tmp_path, flavor
):
    """Exercise real archive bytes with a fake engine, not release qualification."""
    # Keep package construction within Windows PowerShell's path limit even
    # when the source checkout is a nested worktree. Archive checks stay intact.
    package_id = f"arc-{uuid.uuid4().hex[:12]}-{flavor}"
    output_dir = Path(".agent_work") / "pytest-temp" / package_id
    output_path = REPO_ROOT / output_dir
    try:
        result = _run_package_release(
            "-Version",
            package_id,
            "-OutputDir",
            str(output_dir),
            "-Image",
            f"ghcr.io/cdcai/towerscout:{package_id}",
            "-ImageDigest",
            "sha256:" + "1" * 64,
            "-PytorchFlavor",
            flavor,
            "-AllowDirtySource",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        zip_path = output_path / f"towerscout-{package_id}.zip"
        checksum, filename = (
            zip_path.with_suffix(".zip.sha256").read_text().strip().split("  ", 1)
        )
        assert filename == zip_path.name
        assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == checksum

        package_root = tmp_path / "TowerScout extracted package"
        with zipfile.ZipFile(zip_path) as archive:
            files = {
                item.filename.replace("\\", "/"): item
                for item in archive.infolist()
                if not item.is_dir()
            }
            assert not set(DEFERRED_HELPER_FILES).intersection(files)
            required_files = {
                "scripts/lib/TowerScoutHostHelperState.ps1",
                "scripts/lib/TowerScoutCertificateStore.ps1",
                "scripts/repair-provider-tls.cmd",
                "scripts/repair-provider-tls.ps1",
                "scripts/import-tls-ca.cmd",
                "scripts/import-tls-ca.ps1",
                ".env.example",
            }
            assert required_files.issubset(files)
            for license_path in ("licenses/Apache-2.0.txt", "licenses/AGPL-3.0.txt", "licenses/CC-BY-NC-SA-4.0.txt", "licenses/jQuery-MIT.txt", "licenses/SyntheticData-MIT.txt", "licenses/TowerScout-APPLICATION-GRANT.md"):
                assert archive.read(files[license_path]) == (REPO_ROOT / license_path).read_bytes()
            assert 'docs/release/release-notes.md' in files
            assert 'docs/release/task105-candidate-notes.md' not in files
            for name in ('docs/towerscout-user-guide.html', 'docs/v1-rc1-quick-start.html'):
                text = archive.read(files[name]).decode('utf-8-sig')
                for target in re.findall(r'(?:href="|url=)([^"\s>]+)', text):
                    parsed = urlsplit(target)
                    if parsed.scheme or not parsed.path:
                        continue
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
                    assert resolved in files, f'{name}: missing offline link {target}'
            for name, entry in files.items():
                if not name.startswith('docs/') or not name.endswith('.md'):
                    continue
                text = archive.read(entry).decode('utf-8-sig')
                for target in re.findall(r'\]\(<?([^\s)]+)>?\)', text):
                    parsed = urlsplit(target.rstrip('>'))
                    if parsed.scheme or not parsed.path:
                        continue
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
                    assert resolved in files, f'{name}: missing packaged link {target}'
            recorded = {}
            for line in (
                archive.read(files["SHA256SUMS.txt"]).decode("ascii").splitlines()
            ):
                digest, relative = line.split("  ", 1)
                recorded[relative] = digest
                assert (
                    hashlib.sha256(archive.read(files[relative])).hexdigest() == digest
                )
            assert set(recorded) == set(files) - {"SHA256SUMS.txt"}
            manifest = json.loads(archive.read(files["release-manifest.v1.json"]))
            assert_manifest_schema(manifest)
            assert manifest["pytorch_flavor"] == flavor
            archive.extractall(package_root)

        fake_bin = tmp_path / "fake-bin"
        fake_bin.mkdir()
        (fake_bin / "docker.cmd").write_text(
            "@echo off\n"
            'echo %*>>"%TOWERSCOUT_TEST_ENGINE_LOG%"\n'
            'if "%1"=="info" exit /b 0\n'
            'if "%1"=="compose" if "%2"=="version" (\n'
            "  echo Docker Compose version v2.39.4\n"
            "  exit /b 0\n"
            ")\n"
            'if "%1"=="compose" exit /b 7\n'
            'if "%1"=="inspect" exit /b 1\n'
            "exit /b 0\n",
            encoding="ascii",
        )
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
        env["TOWERSCOUT_TEST_ENGINE_LOG"] = str(tmp_path / "engine.log")
        state_dir = package_root / ".towerscout-runtime" / "host-helper"
        state_dir.mkdir(parents=True)
        for review_enabled in ("0", "1"):
            for script_name, arguments in (
                ("launch.ps1", ["-Gpu", "off", "-TimeoutSeconds", "5", "-NoBrowser"]),
                ("stop.ps1", []),
            ):
                for name in (
                    "session-prior.json",
                    "token-prior.secret",
                    "operation-prior.json",
                ):
                    (state_dir / name).write_text(
                        "synthetic stale state", encoding="ascii"
                    )
                env["TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED"] = review_enabled
                env["TOWERSCOUT_HOST_HELPER_ENABLED"] = "1"
                env["TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION"] = "1"
                env["TOWERSCOUT_HOST_HELPER_SESSION_ID"] = "prior"
                env["TOWERSCOUT_HOST_HELPER_SESSION_KEY"] = "synthetic-prior-key"
                run = subprocess.run(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(package_root / "scripts" / script_name),
                        "-Engine",
                        "docker",
                        *arguments,
                    ],
                    cwd=package_root,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=30,
                    check=False,
                )
                assert run.returncode == 7, run.stdout + run.stderr
                assert not list(state_dir.iterdir())
                if review_enabled == "1":
                    assert "host helper is not included in this package" in run.stdout
        engine_log = (tmp_path / "engine.log").read_text()
        assert "up -d" in engine_log
        assert "down --remove-orphans" in engine_log
    finally:
        shutil.rmtree(output_path, ignore_errors=True)
