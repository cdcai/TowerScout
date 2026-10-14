"""Windows provider installation must recover from a failed first attempt."""

import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def make_test_wheel(path: Path) -> None:
    dist_info = "podman_compose-1.5.0.dist-info"
    files = {
        "podman_compose.py": (
            "def main():\n"
            "    print('podman-compose version 1.5.0')\n"
        ),
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\nGenerator: task105-test\n"
            "Root-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        f"{dist_info}/METADATA": (
            "Metadata-Version: 2.1\nName: podman-compose\nVersion: 1.5.0\n"
        ),
    }
    record = "".join(f"{name},,\n" for name in files)
    record += f"{dist_info}/RECORD,,\n"
    with zipfile.ZipFile(path, "w") as archive:
        for name, contents in files.items():
            archive.writestr(name, contents)
        archive.writestr(f"{dist_info}/RECORD", record)


@unittest.skipUnless(os.name == "nt", "Windows PowerShell package test")
class ProviderInstallerTest(unittest.TestCase):
    def test_failed_install_then_ordinary_retry_and_relocated_wrapper(self):
        with tempfile.TemporaryDirectory(prefix="task105-provider-") as temp:
            work = Path(temp)
            python_exe = sys.executable
            scripts = work / "repo" / "scripts"
            lib = scripts / "lib"
            lib.mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/install-podman-compose-provider.ps1", scripts)
            shutil.copy2(ROOT / "scripts/install-podman-compose-provider.cmd", scripts)
            shutil.copy2(ROOT / "scripts/lib/TowerScoutPodmanComposeProvider.ps1", lib)

            wheel = work / "podman_compose-1.5.0-py3-none-any.whl"
            make_test_wheel(wheel)
            class QuietHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(work), **kwargs)

                def log_message(self, format, *args):
                    pass

            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            catalog = {
                "schema_version": 1,
                "providers": [{
                    "id": "podman-compose-pypi-1.5.0",
                    "display_name": "test podman-compose",
                    "source_url": f"http://127.0.0.1:{server.server_port}/{wheel.name}",
                    "package_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                    "requires_python": ">=3.9",
                    "dependencies": [],
                    "windows_amd64_sha256": "",
                    "allowed_executable_names": ["podman-compose.cmd"],
                    "disallowed_path_patterns": [],
                    "required_commands": [{
                        "arguments": ["version"],
                        "expected_output_pattern": "podman-compose version 1\\.5\\.0",
                    }],
                }],
            }
            (scripts / "podman-compose-providers.v1.json").write_text(
                json.dumps(catalog), encoding="utf-8"
            )
            shells = ["powershell.exe"]
            if shutil.which("pwsh"):
                shells.append("pwsh")
            elif os.environ.get("TOWERSCOUT_REQUIRE_PWSH") == "1":
                self.fail("PowerShell 7 is required for the Windows CI provider test")

            for shell in shells:
                with self.subTest(parent=shell):
                    install = work / "repo" / "tools" / "podman-compose-provider" / shell
                    ps_script = f"""
            $ErrorActionPreference = 'Stop'
            if ('{shell}' -eq 'pwsh') {{ $env:PSModulePath = 'C:\\Program Files\\PowerShell\\7\\Modules' }}
            $installer = '{scripts / 'install-podman-compose-provider.cmd'}'
            $install = '{install}'
            & $installer -InstallDir $install -Python 'missing-task105-python' -Apply
            if ($LASTEXITCODE -eq 0) {{ throw 'Expected injected Python failure' }}
            if (Test-Path -LiteralPath $install) {{ throw 'Failed install left a final directory' }}
            New-Item -ItemType Directory -Path $install | Out-Null
            Set-Content -LiteralPath (Join-Path $install 'partial-install-marker.txt') -Value 'preserve-me'
            & $installer -InstallDir $install -Python '{python_exe}' -Apply
            if ($LASTEXITCODE -ne 0) {{ throw 'Normal retry failed' }}
            $backups = @(Get-ChildItem -LiteralPath (Split-Path -Parent $install) -Directory -Filter '.towerscout-provider-previous-*')
            if ($backups.Count -ne 1) {{ throw 'Partial install backup missing' }}
            $marker = Join-Path $backups[0].FullName 'partial-install-marker.txt'
            if (-not (Test-Path -LiteralPath $marker) -or (Get-Content -LiteralPath $marker) -ne 'preserve-me') {{
                throw 'Partial install state was not preserved'
            }}
            $wrapper = Join-Path $install 'podman-compose.cmd'
            $output = & $wrapper version
            if ($LASTEXITCODE -ne 0 -or $output -notmatch 'podman-compose version 1.5.0') {{
                throw 'Promoted wrapper failed after stage relocation'
            }}
            & $installer -InstallDir $install -Python 'missing-task105-python' -Apply
            if ($LASTEXITCODE -ne 0) {{ throw 'Idempotent retry failed' }}
            'ok'
            """
                    encoded = __import__("base64").b64encode(ps_script.encode("utf-16le")).decode("ascii")
                    result = subprocess.run(
                        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
                        text=True,
                        capture_output=True,
                        cwd=ROOT,
                        timeout=180,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
