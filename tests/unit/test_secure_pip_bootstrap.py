"""Bootstrap must reject substituted bytes before invoking the installer."""
import hashlib
import importlib.util
import io
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bootstrap-pip.py"


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("secure_bootstrap", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_corrupted_download_never_runs_pip(tmp_path):
    bootstrap = load_bootstrap()
    with patch.object(bootstrap.urllib.request, "urlopen", return_value=io.BytesIO(b"substituted")), patch.object(bootstrap.subprocess, "run") as run:
        with pytest.raises(ValueError, match="SHA-256"):
            bootstrap.bootstrap(tmp_path)
        run.assert_not_called()
        assert not list(tmp_path.iterdir())


def test_unsupported_python_fails_before_network_or_install(tmp_path):
    bootstrap = load_bootstrap()
    with patch.object(bootstrap.sys, "version_info", (3, 9)), patch.object(bootstrap.urllib.request, "urlopen") as download, patch.object(bootstrap.subprocess, "run") as run:
        with pytest.raises(RuntimeError, match="Python 3.10"):
            bootstrap.bootstrap(tmp_path)
        download.assert_not_called()
        run.assert_not_called()


def test_verified_wheel_is_installed_offline_and_removed(tmp_path):
    bootstrap = load_bootstrap()
    payload = b"synthetic verified wheel"
    with patch.object(bootstrap, "WHEEL_SHA256", hashlib.sha256(payload).hexdigest()), patch.object(bootstrap.urllib.request, "urlopen", return_value=io.BytesIO(payload)), patch.object(bootstrap.subprocess, "run") as run:
        bootstrap.bootstrap(tmp_path)
        command = run.call_args.args[0]
        assert "--no-index" in command and "--no-deps" in command
        assert "--isolated" in command
        assert run.call_args.kwargs["check"] is True
        assert run.call_args.kwargs["timeout"] == 180
        assert not list(tmp_path.iterdir())


def test_install_failure_propagates_and_removes_download(tmp_path):
    bootstrap = load_bootstrap()
    payload = b"synthetic verified wheel"
    failure = bootstrap.subprocess.CalledProcessError(1, "pip")
    with patch.object(bootstrap, "WHEEL_SHA256", hashlib.sha256(payload).hexdigest()), patch.object(bootstrap.urllib.request, "urlopen", return_value=io.BytesIO(payload)), patch.object(bootstrap.subprocess, "run", side_effect=failure):
        with pytest.raises(bootstrap.subprocess.CalledProcessError):
            bootstrap.bootstrap(tmp_path)
        assert not list(tmp_path.iterdir())
