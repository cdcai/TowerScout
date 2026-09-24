"""Windows process-boundary regressions for the packaged runtime."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import psutil
import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutBootstrap.ps1"
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
PODMAN_GPU_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutPodmanGpu.ps1"


def _powershell_executable():
    return shutil.which("powershell.exe") or shutil.which("pwsh")


def _powershell_literal(value: Path | str) -> str:
    return str(value).replace("'", "''")


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_bootstrap_command_drains_large_output_and_preserves_exit_status(tmp_path):
    emitter = tmp_path / "emit-large-output.py"
    emitter.write_text(
        "import sys\n"
        "sys.stdout.write('o' * (256 * 1024))\n"
        "sys.stdout.flush()\n"
        "sys.stderr.write('e' * (256 * 1024))\n"
        "sys.stderr.flush()\n"
        "raise SystemExit(7)\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(BOOTSTRAP_LIB)}'
    $result = Invoke-TowerScoutBootstrapCommand `
        -FileName '{_powershell_literal(sys.executable)}' `
        -Arguments @('{_powershell_literal(emitter)}') `
        -TimeoutSeconds 10
    $result | ConvertTo-Json -Compress
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ExitCode"] == 7
    assert payload["TimedOut"] is False
    assert 0 < len(payload["StdOut"]) <= 64 * 1024
    assert 0 < len(payload["StdErr"]) <= 64 * 1024


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_bootstrap_command_preserves_exact_windows_arguments(tmp_path):
    argument_probe = tmp_path / "capture-arguments.py"
    argument_probe.write_text(
        "import json\n"
        "import sys\n"
        "print(json.dumps(sys.argv[1:]), flush=True)\n",
        encoding="utf-8",
    )
    expected = [
        "plain",
        "value with spaces",
        "",
        "C:\\Program Files\\TowerScout\\",
        'quoted"value',
        "trailing\\",
    ]
    powershell_arguments = ",\n            ".join(
        f"'{_powershell_literal(value)}'" for value in [argument_probe, *expected]
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(BOOTSTRAP_LIB)}'
    $result = Invoke-TowerScoutBootstrapCommand `
        -FileName '{_powershell_literal(sys.executable)}' `
        -Arguments @(
            {powershell_arguments}
        ) `
        -TimeoutSeconds 10
    $result | ConvertTo-Json -Compress
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ExitCode"] == 0
    assert payload["TimedOut"] is False
    assert json.loads(payload["StdOut"]) == expected


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_bootstrap_command_timeout_cleans_up_owned_process_tree(tmp_path):
    child_pid_path = tmp_path / "child.pid"
    parent = tmp_path / "spawn-child.py"
    parent.write_text(
        "import subprocess\n"
        "import sys\n"
        "import time\n"
        "from pathlib import Path\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "Path(sys.argv[1]).write_text(str(child.pid), encoding='ascii')\n"
        "print(child.pid, flush=True)\n"
        "time.sleep(60)\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(BOOTSTRAP_LIB)}'
    $result = Invoke-TowerScoutBootstrapCommand `
        -FileName '{_powershell_literal(sys.executable)}' `
        -Arguments @(
            '{_powershell_literal(parent)}',
            '{_powershell_literal(child_pid_path)}'
        ) `
        -TimeoutSeconds 1
    $result | ConvertTo-Json -Compress
    """
    child_pid = None

    try:
        result = subprocess.run(
            [
                _powershell_executable(),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        assert payload["ExitCode"] == 124
        assert payload["TimedOut"] is True
        assert "timed out after 1 seconds" in payload["StdErr"]
        child_pid = int(child_pid_path.read_text(encoding="ascii"))
        if psutil.pid_exists(child_pid):
            _, alive = psutil.wait_procs([psutil.Process(child_pid)], timeout=5)
            assert not alive, f"Timed-out child process {child_pid} survived cleanup"
    finally:
        if child_pid is None and child_pid_path.is_file():
            child_pid = int(child_pid_path.read_text(encoding="ascii"))
        if child_pid is not None and psutil.pid_exists(child_pid):
            psutil.Process(child_pid).kill()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_podman_command_drains_output_and_preserves_exit_status(tmp_path):
    emitter = tmp_path / "emit-podman-output.py"
    emitter.write_text(
        "import sys\n"
        "sys.stdout.write('o' * (256 * 1024))\n"
        "sys.stdout.flush()\n"
        "sys.stderr.write('e' * (256 * 1024))\n"
        "sys.stderr.flush()\n"
        "raise SystemExit(7)\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(COMPOSE_LIB)}'
    function Resolve-TowerScoutCommandOrPath {{
        param([string] $Value)
        return '{_powershell_literal(sys.executable)}'
    }}
    $result = Invoke-TowerScoutPodmanCommand `
        -Arguments @('{_powershell_literal(emitter)}') `
        -TimeoutSeconds 10
    $result | ConvertTo-Json -Compress
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ExitCode"] == 7
    assert payload["TimedOut"] is False
    assert 0 < len(payload["StdOut"]) <= 64 * 1024
    assert 0 < len(payload["StdErr"]) <= 64 * 1024


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_podman_gpu_command_honors_timeout(tmp_path):
    sleeper = tmp_path / "sleep.py"
    sleeper.write_text(
        "import time\n"
        "time.sleep(3)\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(PODMAN_GPU_LIB)}'
    $result = Invoke-TowerScoutPodmanGpuCommand `
        -FileName '{_powershell_literal(sys.executable)}' `
        -Arguments @('{_powershell_literal(sleeper)}') `
        -TimeoutSeconds 1
    $result | ConvertTo-Json -Compress
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ExitCode"] == 124
    assert payload["TimedOut"] is True
    assert "timed out after 1 seconds" in payload["StdErr"]


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_compose_command_binds_explicit_rootless_podman_connection():
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(COMPOSE_LIB)}'
    function Test-TowerScoutCommand {{ return $true }}
    function Initialize-TowerScoutPodmanComposeProvider {{ return 'approved-provider' }}
    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        if ([string]::Join(' ', $Arguments) -ne 'system connection list --format json') {{
            throw "Unexpected Podman target probe: $([string]::Join(' ', $Arguments))"
        }}
        return [pscustomobject]@{{
            ExitCode = 0
            TimedOut = $false
            StdOut = '[{{"Name":"podman-machine-default","URI":"ssh://user@127.0.0.1:51313/run/user/1000/podman/podman.sock","Default":false}},{{"Name":"podman-machine-default-root","URI":"ssh://root@127.0.0.1:51313/run/podman/podman.sock","Default":true}}]'
            StdErr = ''
        }}
    }}

    $resolved = Get-TowerScoutComposeCommand `
        -Engine podman `
        -PodmanConnectionName 'podman-machine-default'
    if ($resolved.Executable -ne 'podman') {{
        throw "Unexpected executable: $($resolved.Executable)"
    }}
    if ([string]::Join(' ', $resolved.Arguments) -ne '--connection podman-machine-default compose') {{
        throw "Podman connection was not bound: $([string]::Join(' ', $resolved.Arguments))"
    }}
    'ok'
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_compose_command_rejects_root_owned_podman_connection():
    command = f"""
    $ErrorActionPreference = "Stop"
    . '{_powershell_literal(COMPOSE_LIB)}'
    function Test-TowerScoutCommand {{ return $true }}
    function Initialize-TowerScoutPodmanComposeProvider {{ return 'approved-provider' }}
    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        return [pscustomobject]@{{
            ExitCode = 0
            TimedOut = $false
            StdOut = '[{{"Name":"podman-machine-default-root","URI":"ssh://root@127.0.0.1:51313/run/podman/podman.sock","Default":true}}]'
            StdErr = ''
        }}
    }}

    try {{
        Get-TowerScoutComposeCommand `
            -Engine podman `
            -PodmanConnectionName 'podman-machine-default-root' | Out-Null
        throw 'Root-owned Podman connection was accepted.'
    }}
    catch {{
        if ($_.Exception.Message -notmatch 'rootless') {{
            throw
        }}
    }}
    'ok'
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_compose_invocation_carries_rootless_connection_to_cmd_provider(tmp_path):
    captured_arguments = tmp_path / "podman-arguments.txt"
    fake_podman = tmp_path / "podman.cmd"
    fake_podman.write_text(
        "@echo off\r\n"
        f"> \"{captured_arguments}\" echo %*\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    $env:Path = '{_powershell_literal(tmp_path)};' + $env:Path
    . '{_powershell_literal(COMPOSE_LIB)}'
    function Test-TowerScoutCommand {{ return $true }}
    function Initialize-TowerScoutPodmanComposeProvider {{ return 'approved-provider' }}
    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        return [pscustomobject]@{{
            ExitCode = 0
            TimedOut = $false
            StdOut = '[{{"Name":"podman-machine-default","URI":"ssh://user@127.0.0.1:51313/run/user/1000/podman/podman.sock","Default":false}}]'
            StdErr = ''
        }}
    }}
    function Get-TowerScoutPodmanComposeVersionResult {{
        param([hashtable] $Command)
        return [pscustomobject]@{{ ExitCode = 0; Lines = @('podman-compose version 1.5.0') }}
    }}

    Invoke-TowerScoutCompose `
        -Engine podman `
        -PodmanMachineName 'podman-machine-default' `
        -ComposeArguments @('ps')
    if ($script:TowerScoutComposeExitCode -ne 0) {{
        throw "Fake Podman compose exited $script:TowerScoutComposeExitCode"
    }}
    $captured = Get-Content -LiteralPath '{_powershell_literal(captured_arguments)}' -Raw
    if ($captured -notmatch '^--connection podman-machine-default compose ') {{
        throw "Connection was not first in the final Podman arguments: $captured"
    }}
    if ($captured -notmatch [regex]::Escape('compose.yaml') -or $captured -notmatch ' ps\s*$') {{
        throw "Compose file or operation was missing from final arguments: $captured"
    }}
    'ok'
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell runtime helpers are Windows-only")
def test_stale_container_cleanup_carries_rootless_connection(tmp_path):
    captured_arguments = tmp_path / "podman-cleanup-arguments.txt"
    fake_podman = tmp_path / "podman.cmd"
    fake_podman.write_text(
        "@echo off\r\n"
        f">> \"{captured_arguments}\" echo %*\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    command = f"""
    $ErrorActionPreference = "Stop"
    $env:Path = '{_powershell_literal(tmp_path)};' + $env:Path
    . '{_powershell_literal(COMPOSE_LIB)}'
    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        return [pscustomobject]@{{
            ExitCode = 0
            TimedOut = $false
            StdOut = '[{{"Name":"podman-machine-default","URI":"ssh://user@127.0.0.1:51313/run/user/1000/podman/podman.sock","Default":false}}]'
            StdErr = ''
        }}
    }}

    Invoke-TowerScoutContainerStopRemove `
        -EngineName podman `
        -ContainerIds @('abcdef0123456789')
    $captured = @(Get-Content -LiteralPath '{_powershell_literal(captured_arguments)}')
    if ($captured.Count -ne 2) {{
        throw "Expected stop and remove commands, got $($captured.Count): $captured"
    }}
    if ($captured[0] -notmatch '^--connection podman-machine-default container stop abcdef0123456789\s*$') {{
        throw "Stop command did not bind the rootless connection: $($captured[0])"
    }}
    if ($captured[1] -notmatch '^--connection podman-machine-default container rm abcdef0123456789\s*$') {{
        throw "Remove command did not bind the rootless connection: $($captured[1])"
    }}
    'ok'
    """

    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout