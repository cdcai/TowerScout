import base64
import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

import ts_host_helper


REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutHostHelper.ps1"
HELPER_STATE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutHostHelperState.ps1"
HELPER_SCRIPT = REPO_ROOT / "scripts" / "host-helper.ps1"
HELPER_WORKER_SCRIPT = REPO_ROOT / "scripts" / "host-helper-worker.ps1"
STOP_SCRIPT = REPO_ROOT / "scripts" / "stop.ps1"
LAUNCH_SCRIPT = REPO_ROOT / "scripts" / "launch.ps1"
COMPOSE_FILE = REPO_ROOT / "compose.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
EDGE_RESTART_OBSERVER = (
    REPO_ROOT
    / "tests"
    / "frontend"
    / "test_task_087_docker_restart_edge_observer.js"
)
DOCKER_RESTART_DRIVER = (
    REPO_ROOT
    / "tests"
    / "frontend"
    / "invoke_task_087_docker_restart_observer.ps1"
)


def _powershell_executable():
    return shutil.which("powershell.exe") or shutil.which("pwsh")


def _run_powershell_script(script: str) -> subprocess.CompletedProcess[str]:
    powershell = _powershell_executable()
    if powershell is None:
        pytest.skip("PowerShell executable not found")

    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-EncodedCommand",
            encoded,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_host_helper_provider_tls_repair_plan_is_docker_only_and_allowlisted():
    script = HELPER_LIB.read_text(encoding="utf-8")
    stop_script = STOP_SCRIPT.read_text(encoding="utf-8")

    assert (
        '$script:TowerScoutHostHelperProviderTlsRepairConfirmation = '
        '"repair_tls_and_restart"'
    ) in script
    assert "function New-TowerScoutProviderTlsRepairOperationPlan" in script
    assert 'if ($providerValue -notin @("google", "azure"))' in script
    assert '$engine -ne "docker"' in script
    assert '"unsupported_runtime"' in script
    assert '"rejected_confirmation"' in script
    assert '"rejected_unknown_provider"' in script
    assert '$publicProvider = "unknown"' in script
    assert '"scripts\\repair-provider-tls.cmd"' in script
    assert (
        'Arguments = @("-Provider", $providerValue, "-Engine", "docker", '
        '"-Gpu", $gpu, "-Apply")'
    ) in script
    assert '"scripts\\stop.cmd"' in script
    assert '"start.bat"' in script
    assert '"-NoBrowser"' in script
    assert "function New-TowerScoutHostHelperOperationLock" in script
    assert "nonce_fingerprint" in script
    assert '"operation-*.json"' in script
    assert "operation_files_cleared" in script
    assert "provider_tls_repair = $providerTlsRepairEnabled" in script
    assert 'State "capability_disabled"' in script
    assert "$script:TowerScoutHostHelperExecutionEnabledByDefault = $false" in script
    assert 'return (Join-Path $stateDirectory "operation-active.json")' in script
    assert "operation-status-{0}.json" in script
    assert "function Enter-TowerScoutHostHelperPackageMutex" in script
    assert "function Write-TowerScoutHostHelperJsonAtomic" in script
    assert "function Protect-TowerScoutHostHelperStatePath" in script
    assert "$script:TowerScoutHostHelperHeartbeatStaleSeconds = 10" in script
    assert "process_start_time_utc" in script
    assert "last_heartbeat_utc" in script
    assert "function Start-TowerScoutHostHelperOperationWorker" in script
    assert "function Resolve-TowerScoutHostHelperControlledCommand" in script
    assert "function Invoke-TowerScoutHostHelperControlledCommand" in script
    assert "function Invoke-TowerScoutProviderTlsRepairControlledExecution" in script
    assert "function Test-TowerScoutHostHelperRealWrapperContract" in script
    assert "function Get-TowerScoutHostHelperBatchInterpreterPath" in script
    assert "function Get-TowerScoutHostHelperTaskkillPath" in script
    assert "$script:TowerScoutHostHelperLaunchReadinessTimeoutSeconds = 180" in script
    assert "$script:TowerScoutHostHelperStartTimeoutHeadroomSeconds = 60" in script
    assert "function Stop-TowerScoutHostHelperProcessTree" in script
    assert "function Wait-TowerScoutHostHelperOutputTask" in script
    assert '$taskkillPath = Get-TowerScoutHostHelperTaskkillPath' in script
    assert '& $taskkillPath /PID $Process.Id /T /F' in script
    assert "$taskkillExitCode = $LASTEXITCODE" in script
    assert "$exited = $Process.WaitForExit($CleanupTimeoutMs)" in script
    assert "if ($RequireExit -and -not $exited)" in script
    assert (
        "Stop-TowerScoutHostHelperProcessTree -Process $Process -RequireExit"
        in script
    )
    assert "& taskkill.exe" not in script
    assert "$Process.Kill($true)" in script
    assert "Stop-TowerScoutHostHelperProcessTree -Process $process" in script
    assert 'Interpreter = "cmd.exe"' in script
    assert '"real_wrapper_contract_validated"' in script
    assert "executed = $false" in script
    assert "function Get-TowerScoutHostHelperAllowedMethodsForPath" in script
    assert '"Access-Control-Allow-Methods: $AccessControlAllowMethods"' in script
    assert 'return "GET, OPTIONS"' in script
    assert 'return "POST, OPTIONS"' in script
    assert "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION" in script
    assert "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION" in stop_script
    assert "function Test-TowerScoutHostHelperFixedTimeStringEquals" in script
    assert (
        "Test-TowerScoutHostHelperFixedTimeStringEquals `\n"
        "                -Expected $Token `\n"
        "                -Actual $providedToken"
    ) in script
    assert "Set-Acl -LiteralPath $Path -AclObject $security -ErrorAction Stop" in script
    assert "function Get-TowerScoutHostHelperOperationWorkerPath" in script
    assert "function Save-TowerScoutHostHelperOperationWorkerIdentity" in script
    assert "function Test-TowerScoutHostHelperOperationWorkerActive" in script
    assert '"worker_exit"' in script
    assert "[datetime] $DeadlineUtc" in script
    assert "Clear-TowerScoutHostHelperSession" in stop_script


def test_host_helper_review_bridge_is_explicit_and_does_not_persist_session_key():
    launch_script = LAUNCH_SCRIPT.read_text(encoding="utf-8")
    helper_library = HELPER_LIB.read_text(encoding="utf-8")
    compose = COMPOSE_FILE.read_text(encoding="utf-8")
    env_example = ENV_EXAMPLE.read_text(encoding="utf-8")

    assert "function Test-TowerScoutHostHelperReviewEnabled" in helper_library
    assert "TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED" in helper_library
    assert "Initialize-TowerScoutHostHelperReviewSession" in launch_script
    assert "$helperControlledOperation" in launch_script
    assert "if (-not $helperControlledOperation)" in launch_script
    assert (
        "function Test-TowerScoutHostHelperSessionMetadataMatchesProfile"
        in helper_library
    )
    for profile_field in (
        '"state"',
        '"helper_version"',
        '"engine"',
        '"gpu"',
        '"app_port"',
        '"helper_port"',
        '"package_flavor"',
        '"package_root_identity"',
    ):
        assert profile_field in helper_library
    assert "Get-TowerScoutHostHelperPackageRootIdentity" in helper_library
    assert "function Test-TowerScoutHostHelperSessionLiveness" in helper_library
    assert "process_start_time_utc" in helper_library
    assert "last_heartbeat_utc" in helper_library
    assert "lease_expires_at_utc" in helper_library
    assert "function Start-TowerScoutHostHelperReviewProcess" in helper_library
    assert "-PassThru" in helper_library
    assert "-Process $helperProcess" in helper_library
    assert "$metadataProcessId -eq $helperProcess.Id" in helper_library
    assert "host-helper-visible.cmd" not in helper_library
    assert "host-helper-visible.cmd" not in launch_script
    assert "& $visibleHelper" not in launch_script
    assert "TOWERSCOUT_HOST_HELPER_SESSION_KEY" in helper_library
    assert "Clear-TowerScoutHostHelperBridgeEnvironment" in helper_library
    assert "function Invoke-TowerScoutLaunchRuntime" in launch_script
    assert 'if ($MyInvocation.InvocationName -eq ".")' in launch_script
    assert "finally {" in launch_script
    assert "if (-not $launchSucceeded)" in launch_script
    assert "-SessionId ([string] $hostHelperReviewSession.SessionId)" in launch_script
    assert "-Process $hostHelperReviewSession.Process" in launch_script
    assert (
        "TOWERSCOUT_HOST_HELPER_ENABLED: ${TOWERSCOUT_HOST_HELPER_ENABLED:-0}"
        in compose
    )
    assert "TOWERSCOUT_HOST_PORT: ${TOWERSCOUT_PORT:-5000}" in compose
    assert (
        "TOWERSCOUT_HOST_HELPER_SESSION_KEY: "
        "${TOWERSCOUT_HOST_HELPER_SESSION_KEY:-}"
        in compose
    )
    assert "TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED=0" in env_example
    assert "TOWERSCOUT_HOST_HELPER_SESSION_KEY=" not in env_example
    assert "do not put those values in" in env_example


def test_edge_restart_observer_and_docker_driver_are_constrained():
    observer = EDGE_RESTART_OBSERVER.read_text(encoding="utf-8")
    driver = DOCKER_RESTART_DRIVER.read_text(encoding="utf-8")

    assert "normalizeLoopbackUrl" in observer
    assert "new AbortController()" in observer
    assert "sessionStorage.setItem" in observer
    assert "assert.strictEqual(recoveredState, initialState)" in observer
    assert "assert.strictEqual(alternateState, initialState)" in observer
    assert "TOWERSCOUT_EXPECTED_READINESS_STATE" in observer
    assert "TOWERSCOUT_BROWSER_PID_SIGNAL" in observer
    assert "TOWERSCOUT_BROWSER_PROFILE_DIR" in observer
    assert "userDataDir: BROWSER_PROFILE_DIR" in observer
    assert "browser.process()" in observer
    assert "--no-sandbox" not in observer
    assert "--disable-setuid-sandbox" not in observer
    assert "orchestration: 'external'" in observer

    assert '^towerscout-task087-[a-z0-9][a-z0-9-]*$' in driver
    assert "com.docker.compose.project=$ProjectName" in driver
    assert "com.docker.compose.service=towerscout" in driver
    assert "127.0.0.1:$AppPort" in driver
    assert "compose -p $ProjectName -f $composePath stop towerscout" in driver
    assert "compose -p $ProjectName -f $composePath start towerscout" in driver
    assert "function Stop-Task087ProcessTree" in driver
    assert "& $taskkill.Source /PID $Process.Id /T /F" in driver
    assert "$exited = $Process.WaitForExit($TimeoutMilliseconds)" in driver
    assert "$serviceNeedsRestore = $true" in driver
    assert (
        "Assert-Task087ContainerIdentity -ContainerId $containerId -RequireRunning"
        in driver
    )
    assert "$serviceNeedsRestore = $false" in driver
    assert "Stop-Task087ProcessTree -Process $observer" in driver
    assert "Stop-Task087ProcessTree -Process $browserProcess" in driver
    assert "$browserProfilePath" in driver
    assert "$savedEnvironment" in driver
    assert "$observer.Kill()" not in driver
    assert "down" not in driver
    assert "rm -f" not in driver


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_launcher_starts_and_supervises_the_real_long_lived_helper():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        $ProgressPreference = "SilentlyContinue"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("TowerScout Task 087 launcher {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $session = $null
        try {{
            $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED = "1"
            $watch = [System.Diagnostics.Stopwatch]::StartNew()
            $session = Initialize-TowerScoutHostHelperReviewSession `
                -EngineName "docker" `
                -GpuMode "off" `
                -AppPort 5000 `
                -RootPath $root `
                -PackageFlavor "launcher-probe"
            $watch.Stop()
            $metadata = Get-TowerScoutHostHelperSessionMetadata `
                -SessionId ([string] $session.SessionId) `
                -RootPath $root
            [pscustomobject]@{{
                elapsed_ms = [int] $watch.ElapsedMilliseconds
                started_new_process = [bool] $session.StartedNewProcess
                process_alive = -not $session.Process.HasExited
                metadata_process_id = [int] $metadata.process_id
                process_id = [int] $session.Process.Id
                profile_matches = Test-TowerScoutHostHelperSessionMetadataMatchesProfile `
                    -Metadata $metadata `
                    -EngineName "docker" `
                    -GpuMode "off" `
                    -AppPort 5000 `
                    -RootPath $root `
                    -PackageFlavor "launcher-probe"
                authenticated_liveness = Test-TowerScoutHostHelperSessionLiveness `
                    -Metadata $metadata `
                    -SessionId ([string] $session.SessionId) `
                    -RootPath $root `
                    -AppPort 5000
                helper_port_exported = [int] $env:TOWERSCOUT_HOST_HELPER_PORT -gt 0
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if ($null -ne $session) {{
                Stop-TowerScoutHostHelperReviewSession `
                    -RootPath $root `
                    -SessionId ([string] $session.SessionId) `
                    -Process $session.Process
                $session.Process.Dispose()
            }}
            Remove-Item Env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("{"))
    )
    assert payload["elapsed_ms"] < 15000
    assert payload["started_new_process"] is True
    assert payload["process_alive"] is True
    assert payload["metadata_process_id"] == payload["process_id"]
    assert payload["profile_matches"] is True
    assert payload["authenticated_liveness"] is True
    assert payload["helper_port_exported"] is True


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_launcher_start_failure_clears_exact_session_and_bridge_environment():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("TowerScout Task 087 failed start {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        try {{
            $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED = "1"
            function Start-TowerScoutHostHelperReviewProcess {{
                param(
                    [string] $EngineName,
                    [string] $GpuMode,
                    [int] $AppPort,
                    [string] $RootPath,
                    [string] $PackageFlavor,
                    [string] $SessionId,
                    [int] $MutexWaitMilliseconds
                )
                throw "simulated process start failure"
            }}
            $failed = $false
            try {{
                Initialize-TowerScoutHostHelperReviewSession `
                    -EngineName "docker" `
                    -GpuMode "off" `
                    -AppPort 5000 `
                    -RootPath $root `
                    -PackageFlavor "failed-start-probe" | Out-Null
            }}
            catch {{
                $failed = $true
            }}
            $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $root
            [pscustomobject]@{{
                failed = $failed
                enabled = [string] $env:TOWERSCOUT_HOST_HELPER_ENABLED
                has_port = Test-Path Env:TOWERSCOUT_HOST_HELPER_PORT
                has_session_id = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_ID
                has_session_key = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY
                session_files = @(
                    Get-ChildItem -LiteralPath $stateDirectory -Filter "session-*.json" -ErrorAction SilentlyContinue
                ).Count
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            Remove-Item Env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("{"))
    )
    assert payload == {
        "failed": True,
        "enabled": "0",
        "has_port": False,
        "has_session_id": False,
        "has_session_key": False,
        "session_files": 0,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_launcher_detects_early_helper_exit_without_waiting_for_deadline():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("TowerScout Task 087 early exit {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        try {{
            $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED = "1"
            function Start-TowerScoutHostHelperReviewProcess {{
                param(
                    [string] $EngineName,
                    [string] $GpuMode,
                    [int] $AppPort,
                    [string] $RootPath,
                    [string] $PackageFlavor,
                    [string] $SessionId,
                    [int] $MutexWaitMilliseconds
                )
                return Start-Process `
                    -FilePath "powershell.exe" `
                    -ArgumentList @("-NoProfile", "-Command", "exit 23") `
                    -WindowStyle Hidden `
                    -PassThru
            }}
            $watch = [System.Diagnostics.Stopwatch]::StartNew()
            $failed = $false
            try {{
                Initialize-TowerScoutHostHelperReviewSession `
                    -EngineName "docker" `
                    -GpuMode "off" `
                    -AppPort 5000 `
                    -RootPath $root `
                    -PackageFlavor "early-exit-probe" `
                    -ReadinessTimeoutSeconds 10 | Out-Null
            }}
            catch {{
                $failed = $true
            }}
            $watch.Stop()
            [pscustomobject]@{{
                failed = $failed
                elapsed_ms = [int] $watch.ElapsedMilliseconds
                enabled = [string] $env:TOWERSCOUT_HOST_HELPER_ENABLED
                has_port = Test-Path Env:TOWERSCOUT_HOST_HELPER_PORT
                has_session_id = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_ID
                has_session_key = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            Remove-Item Env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("{"))
    )
    assert payload["failed"] is True
    assert payload["elapsed_ms"] < 5000
    assert payload["enabled"] == "0"
    assert payload["has_port"] is False
    assert payload["has_session_id"] is False
    assert payload["has_session_key"] is False


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_launcher_timeout_kills_late_start_before_it_can_publish_state():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("TowerScout Task 087 late start {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $fakeHelper = Join-Path $root "late helper.ps1"
        Set-Content -LiteralPath $fakeHelper -Encoding ASCII -Value @(
            'param(',
            '  [string] $Engine,',
            '  [string] $Gpu,',
            '  [int] $AppPort,',
            '  [string] $PackageFlavor,',
            '  [string] $HelperSessionId,',
            '  [string] $PackageRoot,',
            '  [int] $MutexWaitMilliseconds',
            ')',
            'Set-Content -LiteralPath (Join-Path $PackageRoot "late-pid.txt") -Value $PID',
            'Start-Sleep -Seconds 30',
            'Set-Content -LiteralPath (Join-Path $PackageRoot "late-marker.txt") -Value "late"'
        )
        try {{
            $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED = "1"
            function Start-TowerScoutHostHelperReviewProcess {{
                param(
                    [string] $EngineName,
                    [string] $GpuMode,
                    [int] $AppPort,
                    [string] $RootPath,
                    [string] $PackageFlavor,
                    [string] $SessionId,
                    [int] $MutexWaitMilliseconds
                )
                $arguments = @(
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    $fakeHelper,
                    "-Engine",
                    $EngineName,
                    "-Gpu",
                    $GpuMode,
                    "-AppPort",
                    "$AppPort",
                    "-PackageFlavor",
                    $PackageFlavor,
                    "-HelperSessionId",
                    $SessionId,
                    "-PackageRoot",
                    $RootPath,
                    "-MutexWaitMilliseconds",
                    "$MutexWaitMilliseconds"
                )
                $argumentLine = [string]::Join(
                    " ",
                    @($arguments | ForEach-Object {{
                        ConvertTo-TowerScoutHostHelperCmdArgument -Value ([string] $_)
                    }})
                )
                $startedProcess = Start-Process `
                    -FilePath "powershell.exe" `
                    -ArgumentList $argumentLine `
                    -WindowStyle Hidden `
                    -PassThru
                $script:lateStartedProcessId = $startedProcess.Id
                $pidPath = Join-Path $RootPath "late-pid.txt"
                $pidDeadline = (Get-Date).AddSeconds(3)
                while (-not (Test-Path -LiteralPath $pidPath)) {{
                    if ($startedProcess.HasExited) {{
                        throw "The late-start fixture exited before publishing its PID."
                    }}
                    if ((Get-Date) -ge $pidDeadline) {{
                        Stop-TowerScoutHostHelperProcessTree `
                            -Process $startedProcess `
                            -RequireExit | Out-Null
                        throw "The late-start fixture did not publish its PID."
                    }}
                    Start-Sleep -Milliseconds 50
                }}
                [int] $publishedPid = Get-Content -LiteralPath $pidPath -Raw
                if ($publishedPid -ne $startedProcess.Id) {{
                    throw "The late-start fixture published an unexpected PID."
                }}
                return $startedProcess
            }}
            $timedOut = $false
            try {{
                Initialize-TowerScoutHostHelperReviewSession `
                    -EngineName "docker" `
                    -GpuMode "off" `
                    -AppPort 5000 `
                    -RootPath $root `
                    -PackageFlavor "late-start-probe" `
                    -ReadinessTimeoutSeconds 1 `
                    -MutexWaitMilliseconds 500 | Out-Null
            }}
            catch {{
                $timedOut = $true
            }}
            Start-Sleep -Milliseconds 500
            $lateProcessAlive = $false
            $pidPath = Join-Path $root "late-pid.txt"
            $latePidWritten = Test-Path -LiteralPath $pidPath
            $latePidMatches = $false
            if (Test-Path -LiteralPath $pidPath) {{
                [int] $latePid = Get-Content -LiteralPath $pidPath -Raw
                $latePidMatches = $latePid -eq $script:lateStartedProcessId
                try {{
                    Get-Process -Id $latePid -ErrorAction Stop | Out-Null
                    $lateProcessAlive = $true
                }}
                catch {{}}
            }}
            $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $root
            [pscustomobject]@{{
                timed_out = $timedOut
                late_pid_written = $latePidWritten
                late_pid_matches = $latePidMatches
                late_process_alive = $lateProcessAlive
                late_marker_written = Test-Path -LiteralPath (Join-Path $root "late-marker.txt")
                enabled = [string] $env:TOWERSCOUT_HOST_HELPER_ENABLED
                has_port = Test-Path Env:TOWERSCOUT_HOST_HELPER_PORT
                has_session_id = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_ID
                has_session_key = Test-Path Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY
                session_files = @(
                    Get-ChildItem -LiteralPath $stateDirectory -Filter "session-*.json" -ErrorAction SilentlyContinue
                ).Count
                token_files = @(
                    Get-ChildItem -LiteralPath $stateDirectory -Filter "token-*.secret" -ErrorAction SilentlyContinue
                ).Count
                operation_files = @(
                    Get-ChildItem -LiteralPath $stateDirectory -Filter "operation-*.json" -ErrorAction SilentlyContinue
                ).Count
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            Remove-Item Env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("{"))
    )
    assert payload == {
        "timed_out": True,
        "late_pid_written": True,
        "late_pid_matches": True,
        "late_process_alive": False,
        "late_marker_written": False,
        "enabled": "0",
        "has_port": False,
        "has_session_id": False,
        "has_session_key": False,
        "session_files": 0,
        "token_files": 0,
        "operation_files": 0,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_process_tree_cleanup_falls_back_and_verifies_exit_when_taskkill_fails():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("TowerScout Task 087 taskkill {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $fakeTaskkill = Join-Path $root "taskkill failure.cmd"
        Set-Content -LiteralPath $fakeTaskkill -Encoding ASCII -Value '@exit /b 5'
        $process = $null
        try {{
            function Get-TowerScoutHostHelperTaskkillPath {{
                return $fakeTaskkill
            }}
            $process = Start-Process `
                -FilePath "powershell.exe" `
                -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 30"' `
                -WindowStyle Hidden `
                -PassThru
            $cleanup = Stop-TowerScoutHostHelperProcessTree `
                -Process $process `
                -CleanupTimeoutMs 5000 `
                -RequireExit
            [pscustomobject]@{{
                exited = $cleanup.Exited
                taskkill_exit_code = $cleanup.TaskkillExitCode
                fallback_attempted = $cleanup.FallbackAttempted
                process_has_exited = $process.HasExited
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if ($null -ne $process) {{
                if (-not $process.HasExited) {{
                    $process.Kill()
                    $process.WaitForExit(5000) | Out-Null
                }}
                $process.Dispose()
            }}
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("{"))
    )
    assert payload == {
        "exited": True,
        "taskkill_exit_code": 5,
        "fallback_attempted": True,
        "process_has_exited": True,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_real_launcher_runtime_failure_matrix_cleans_only_failed_launches():
    launch_path = str(LAUNCH_SCRIPT).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{launch_path}'

        function Initialize-TowerScoutHostHelperReviewSession {{
            return [pscustomobject]@{{
                SessionId = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                Process = $null
            }}
        }}
        function Stop-TowerScoutHostHelperReviewSession {{
            $script:cleanupCount += 1
        }}
        function Invoke-TowerScoutCompose {{
            if ($script:scenario -eq "compose_exception") {{
                throw "synthetic exception after helper initialization"
            }}
            $script:TowerScoutComposeExitCode = if (
                $script:scenario -eq "compose_nonzero"
            ) {{ 7 }} else {{ 0 }}
        }}
        function Write-TowerScoutHostDiagnostics {{}}
        function Write-TowerScoutReadinessSummary {{}}
        function Test-TowerScoutCudaSelected {{ return $true }}
        function Get-TowerScoutReadiness {{
            if ($script:scenario -eq "fatal") {{
                return [pscustomobject]@{{
                    Reachable = $true
                    State = "fatal"
                    Payload = [pscustomobject]@{{ state = "fatal" }}
                }}
            }}
            if ($script:scenario -eq "timeout") {{
                return [pscustomobject]@{{
                    Reachable = $false
                    State = "unreachable"
                    Payload = $null
                }}
            }}
            return [pscustomobject]@{{
                Reachable = $true
                State = "ready"
                Payload = [pscustomobject]@{{ state = "ready" }}
            }}
        }}
        function Start-Process {{
            throw "synthetic browser launch failure"
        }}

        $results = @()
        foreach ($case in @(
            [pscustomobject]@{{ Name = "compose_nonzero"; Expected = 7; NoBrowser = $true }},
            [pscustomobject]@{{ Name = "compose_exception"; Expected = -1; NoBrowser = $true }},
            [pscustomobject]@{{ Name = "fatal"; Expected = 1; NoBrowser = $true }},
            [pscustomobject]@{{ Name = "timeout"; Expected = 2; NoBrowser = $true }},
            [pscustomobject]@{{ Name = "browser_failure"; Expected = 0; NoBrowser = $false }},
            [pscustomobject]@{{ Name = "success"; Expected = 0; NoBrowser = $true }}
        )) {{
            $script:scenario = $case.Name
            $script:cleanupCount = 0
            $threw = $false
            $exitCode = -1
            try {{
                $exitCode = Invoke-TowerScoutLaunchRuntime `
                    -EngineName "docker" `
                    -GpuMode "off" `
                    -AppPort 5000 `
                    -RootPath $PWD.Path `
                    -PackageFlavor "source" `
                    -AppUrl "http://localhost:5000" `
                    -ReadinessUrl "http://localhost:5000/api/readiness" `
                    -ReadinessTimeoutSeconds 1 `
                    -NoBrowser:$case.NoBrowser
            }}
            catch {{
                $threw = $true
            }}
            $results += [pscustomobject]@{{
                name = $case.Name
                exit_code = [int] $exitCode
                threw = $threw
                cleanup_count = [int] $script:cleanupCount
            }}
        }}
        $results | ConvertTo-Json -Compress
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(
        next(line for line in result.stdout.splitlines() if line.startswith("["))
    )
    assert payload == [
        {
            "name": "compose_nonzero",
            "exit_code": 7,
            "threw": False,
            "cleanup_count": 1,
        },
        {
            "name": "compose_exception",
            "exit_code": -1,
            "threw": True,
            "cleanup_count": 1,
        },
        {
            "name": "fatal",
            "exit_code": 1,
            "threw": False,
            "cleanup_count": 1,
        },
        {
            "name": "timeout",
            "exit_code": 2,
            "threw": False,
            "cleanup_count": 1,
        },
        {
            "name": "browser_failure",
            "exit_code": 0,
            "threw": False,
            "cleanup_count": 0,
        },
        {
            "name": "success",
            "exit_code": 0,
            "threw": False,
            "cleanup_count": 0,
        },
    ]


def test_host_helper_validates_python_issued_browser_authorization():
    session_key = "A" * 43
    session_id = "a" * 32
    config = ts_host_helper.HostHelperBridgeConfig(
        helper_port=50123,
        helper_session_id=session_id,
        session_authorization_key=session_key,
    )
    authorization = ts_host_helper.issue_browser_authorization(
        config,
        scope="provider_tls_repair",
        provider="google",
        ttl_seconds=120,
    )["authorization"]
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . "{HELPER_LIB}"
        $profile = New-TowerScoutHostHelperRuntimeProfile `
            -Engine "docker" `
            -Gpu "off" `
            -AppPort 5000 `
            -PackageRoot "{REPO_ROOT}" `
            -HelperSessionId "{session_id}" `
            -BrowserAuthorizationKey "{session_key}"
        $result = Resolve-TowerScoutHostHelperBrowserAuthorization `
            -Profile $profile `
            -Authorization "{authorization}" `
            -ExpectedScope "provider_tls_repair" `
            -ExpectedProvider "google"
        $result | ConvertTo-Json -Compress
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["Accepted"] is True
    assert payload["State"] == "authorized"
    assert payload["Provider"] == "google"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_accepts_python_issued_probe_through_loopback_request_handler():
    session_key = "B" * 43
    session_id = "b" * 32
    config = ts_host_helper.HostHelperBridgeConfig(
        helper_port=50124,
        helper_session_id=session_id,
        session_authorization_key=session_key,
    )
    authorization = ts_host_helper.issue_browser_authorization(
        config,
        scope="helper_probe",
        provider="google",
        ttl_seconds=60,
    )["authorization"]
    unknown_operation_id = "c" * 32
    status_authorization = ts_host_helper.issue_browser_authorization(
        config,
        scope="operation_status",
        provider="google",
        operation_id=unknown_operation_id,
        ttl_seconds=120,
    )["authorization"]
    start_authorization = ts_host_helper.issue_browser_authorization(
        config,
        scope="provider_tls_repair",
        provider="google",
        ttl_seconds=120,
    )["authorization"]
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ErrorActionPreference = "Stop"
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-browser-probe-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $listener = $null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile `
                -Engine "docker" `
                -Gpu "off" `
                -AppPort 5000 `
                -PackageRoot $root `
                -HelperSessionId "{session_id}" `
                -BrowserAuthorizationKey "{session_key}" `
                -ProviderTlsRepairEnabled:$true
            $serverToken = New-TowerScoutHostHelperToken
            Save-TowerScoutHostHelperSession -Profile $profile -Token $serverToken | Out-Null
            $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0)
            $listener.Start()
            $response = Invoke-TowerScoutHostHelperSelfTestRequest `
                -Listener $listener `
                -Profile $profile `
                -ServerToken $serverToken `
                -BrowserAuthorization "{authorization}"
            $rejected = Invoke-TowerScoutHostHelperSelfTestRequest `
                -Listener $listener `
                -Profile $profile `
                -ServerToken $serverToken `
                -BrowserAuthorization "v1.invalid.invalid"
            $unknownOperation = Invoke-TowerScoutHostHelperSelfTestRequest `
                -Listener $listener `
                -Profile $profile `
                -ServerToken $serverToken `
                -Path "/operations/{unknown_operation_id}" `
                -BrowserAuthorization "{status_authorization}"
            $startBody = @{{
                provider = "google"
                confirmation = "repair_tls_and_restart"
                operation_authorization = "{start_authorization}"
            }} | ConvertTo-Json -Compress
            $startOperation = Invoke-TowerScoutHostHelperSelfTestRequest `
                -Listener $listener `
                -Profile $profile `
                -ServerToken $serverToken `
                -Path "/operations/provider-tls-repair" `
                -Method "POST" `
                -Body $startBody
            [pscustomobject]@{{
                status_code = [int] $response.StatusCode
                cors_origin = [string] $response.Headers["access-control-allow-origin"]
                rejected_status_code = [int] $rejected.StatusCode
                unknown_operation_status_code = [int] $unknownOperation.StatusCode
                start_operation_status_code = [int] $startOperation.StatusCode
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if ($null -ne $listener) {{
                $listener.Stop()
            }}
            Clear-TowerScoutHostHelperSession -RootPath $root -SessionId "{session_id}" | Out-Null
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "status_code": 200,
        "cors_origin": "http://localhost:5000",
        "rejected_status_code": 401,
        "unknown_operation_status_code": 404,
        "start_operation_status_code": 202,
    }


def test_host_helper_provider_tls_repair_operation_api_is_bounded_and_non_mutating():
    script = HELPER_LIB.read_text(encoding="utf-8")

    assert "$script:TowerScoutHostHelperMaxBodyBytes = 4096" in script
    assert "$script:TowerScoutHostHelperOperationAuthorizationPattern" in script
    assert "$script:TowerScoutHostHelperSignedAuthorizationPattern" in script
    assert "function Resolve-TowerScoutHostHelperBrowserAuthorization" in script
    assert "X-TowerScout-Operation-Authorization" in script
    assert "function Read-TowerScoutProviderTlsRepairRequestBody" in script
    assert "function New-TowerScoutProviderTlsRepairOperationPlanResponse" in script
    assert "function Get-TowerScoutHostHelperOperationStatus" in script
    assert "function ConvertTo-TowerScoutHostHelperScriptExitState" in script
    assert "function Test-TowerScoutHostHelperAsciiBytes" in script
    assert 'if ($method -eq "POST")' in script
    assert '"The helper POST request did not include a content length."' in script
    assert '"The helper request body was too large."' in script
    assert '"The helper request body must be ASCII."' in script
    assert "New-Object byte[] $contentLength" in script
    assert "New-Object char[] $contentLength" not in script
    assert "$contentTypeBase -ne \"application/json\"" in script
    assert "[System.Text.Encoding]::UTF8.GetByteCount($bodyText)" in script
    assert '"json_body_too_large"' in script
    assert '"Content-Length:' in script
    assert '"Content-Type:' in script
    assert '"/operations/provider-tls-repair"' in script
    assert '$operationStatusPathPattern = "^/operations/([a-f0-9]{32})$"' in script
    assert "execution_enabled = $ExecutionEnabled" in script
    assert '"operation_authorization"' in script
    assert '"rejected_operation_authorization"' in script
    assert '"rejected_unexpected_field"' in script
    assert '"operation_exists"' in script
    assert '"tls_repair_completed"' in script
    assert '"readiness_timeout"' in script
    assert '"operation_timeout"' in script
    assert "classification = $Classification" in script
    assert "next_action = $NextAction" in script
    assert "RedirectStandardOutput = $true" in script
    assert "RedirectStandardError = $true" in script


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_operation_request_api_direct_invocation_is_non_mutating():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-api-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "api-probe" -ProviderTlsRepairEnabled:$true
            $authorization = New-TowerScoutHostHelperToken
            $request = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = $authorization }} | ConvertTo-Json -Compress)
            }}
            $disabledProfile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "api-probe"
            $capabilityDisabled = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $disabledProfile -Request $request
            $planned = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $request
            $status = Get-TowerScoutHostHelperOperationStatus -Profile $profile -OperationId ([string] $planned.Body.operation_id)
            $same = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $request
            $otherRequest = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = (New-TowerScoutHostHelperToken) }} | ConvertTo-Json -Compress)
            }}
            $busy = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $otherRequest
            $unexpectedRequest = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = (New-TowerScoutHostHelperToken); restart_mode = "restart_now" }} | ConvertTo-Json -Compress)
            }}
            $unexpected = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $unexpectedRequest
            $executionEnabledRequest = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = (New-TowerScoutHostHelperToken); execution_enabled = $true }} | ConvertTo-Json -Compress)
            }}
            $executionEnabledRejected = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $executionEnabledRequest
            $badAuthorizationRequest = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = "short" }} | ConvertTo-Json -Compress)
            }}
            $badAuthorization = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $badAuthorizationRequest
            $expiredRecord = Get-TowerScoutHostHelperOperationStatusRecord -Profile $profile -OperationId ([string] $planned.Body.operation_id)
            Set-TowerScoutHostHelperObjectValue -InputObject $expiredRecord -Name "expires_at_utc" -Value ((Get-Date).ToUniversalTime().AddSeconds(-1).ToString("o"))
            Write-TowerScoutHostHelperJsonAtomic -Path (Get-TowerScoutHostHelperOperationStatusPath -Profile $profile -OperationId ([string] $planned.Body.operation_id)) -Value $expiredRecord
            Write-TowerScoutHostHelperJsonAtomic -Path (Get-TowerScoutHostHelperOperationLockPath -Profile $profile) -Value $expiredRecord
            $expired = Get-TowerScoutHostHelperOperationStatus -Profile $profile -OperationId ([string] $planned.Body.operation_id)
            $exitStates = [pscustomobject]@{{
                repair_success = ConvertTo-TowerScoutHostHelperScriptExitState -Step "repair" -ExitCode 0
                repair_selection_required = ConvertTo-TowerScoutHostHelperScriptExitState -Step "repair" -ExitCode 2
                repair_failed = ConvertTo-TowerScoutHostHelperScriptExitState -Step "repair" -ExitCode 1
                stop_success = ConvertTo-TowerScoutHostHelperScriptExitState -Step "stop" -ExitCode 0
                stop_failed = ConvertTo-TowerScoutHostHelperScriptExitState -Step "stop" -ExitCode 1
                start_success = ConvertTo-TowerScoutHostHelperScriptExitState -Step "start" -ExitCode 0
                start_timeout = ConvertTo-TowerScoutHostHelperScriptExitState -Step "start" -ExitCode 2
                start_failed = ConvertTo-TowerScoutHostHelperScriptExitState -Step "start" -ExitCode 1
                readiness_success = ConvertTo-TowerScoutHostHelperScriptExitState -Step "readiness" -ExitCode 0
                readiness_timeout = ConvertTo-TowerScoutHostHelperScriptExitState -Step "readiness" -ExitCode 2
                readiness_failed = ConvertTo-TowerScoutHostHelperScriptExitState -Step "readiness" -ExitCode 1
                timed_out = ConvertTo-TowerScoutHostHelperScriptExitState -Step "repair" -ExitCode 1 -TimedOut:$true
            }}
            [pscustomobject]@{{
                capability_disabled_status = $capabilityDisabled.StatusCode
                capability_disabled_state = [string] $capabilityDisabled.Body.state
                planned_status = $planned.StatusCode
                planned_state = [string] $planned.Body.state
                execution_enabled = [bool] $planned.Body.execution_enabled
                status_poll = $status.StatusCode
                same_authorization = $same.StatusCode
                same_existing = [bool] $same.Body.existing_operation
                different_authorization = $busy.StatusCode
                different_state = [string] $busy.Body.state
                different_classification = [string] $busy.Body.classification
                different_terminal = [bool] $busy.Body.terminal
                different_next_action = [string] $busy.Body.next_action
                unexpected_field = $unexpected.StatusCode
                unexpected_state = [string] $unexpected.Body.state
                execution_enabled_field = $executionEnabledRejected.StatusCode
                execution_enabled_field_state = [string] $executionEnabledRejected.Body.state
                bad_authorization = $badAuthorization.StatusCode
                bad_authorization_state = [string] $badAuthorization.Body.state
                expired_state = [string] $expired.Body.state
                expired_classification = [string] $expired.Body.classification
                expired_terminal = [bool] $expired.Body.terminal
                expired_lock_released = $null -eq (Get-TowerScoutHostHelperOperationLock -Profile $profile)
                exit_states = $exitStates
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "capability_disabled_status": 403,
        "capability_disabled_state": "capability_disabled",
        "planned_status": 202,
        "planned_state": "planned",
        "execution_enabled": False,
        "status_poll": 200,
        "same_authorization": 202,
        "same_existing": True,
        "different_authorization": 409,
        "different_state": "operation_busy",
        "different_classification": "active",
        "different_terminal": False,
        "different_next_action": "poll_existing_operation",
        "unexpected_field": 400,
        "unexpected_state": "rejected_unexpected_field",
        "execution_enabled_field": 400,
        "execution_enabled_field_state": "rejected_unexpected_field",
        "bad_authorization": 400,
        "bad_authorization_state": "rejected_operation_authorization",
        "expired_state": "operation_timeout",
        "expired_classification": "terminal_timeout",
        "expired_terminal": True,
        "expired_lock_released": True,
        "exit_states": {
            "repair_success": "tls_repair_completed",
            "repair_selection_required": "tls_repair_selection_required",
            "repair_failed": "tls_repair_failed",
            "stop_success": "runtime_stopped",
            "stop_failed": "runtime_stop_failed",
            "start_success": "ready",
            "start_timeout": "readiness_timeout",
            "start_failed": "runtime_start_failed",
            "readiness_success": "ready",
            "readiness_timeout": "readiness_timeout",
            "readiness_failed": "readiness_failed",
            "timed_out": "operation_timeout",
        },
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_operation_start_returns_before_test_worker_completion():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-async-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $listener = $null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile `
                -Engine "docker" `
                -Gpu "off" `
                -AppPort 5000 `
                -PackageRoot $root `
                -PackageFlavor "async-probe" `
                -ProviderTlsRepairEnabled:$true
            $serverToken = New-TowerScoutHostHelperToken
            $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0)
            $listener.Start()
            $body = @{{
                provider = "google"
                confirmation = "repair_tls_and_restart"
                operation_authorization = (New-TowerScoutHostHelperToken)
            }} | ConvertTo-Json -Compress
            $workerStarter = {{
                param($WorkerProfile, $WorkerPlan)
                Start-Process `
                    -FilePath "powershell.exe" `
                    -ArgumentList @("-NoProfile", "-Command", "Start-Sleep -Seconds 3") `
                    -WindowStyle Hidden | Out-Null
            }}
            $watch = [System.Diagnostics.Stopwatch]::StartNew()
            $accepted = Invoke-TowerScoutHostHelperSelfTestRequest `
                -Listener $listener `
                -Profile $profile `
                -ServerToken $serverToken `
                -RequestToken $serverToken `
                -Path "/operations/provider-tls-repair" `
                -Method "POST" `
                -Body $body `
                -ExecutionEnabled:$true `
                -WorkerStarter $workerStarter
            $watch.Stop()
            $acceptedOperationId = Get-TowerScoutHostHelperObjectValue -InputObject $accepted.Body -Name "operation_id"
            $status = if (-not [string]::IsNullOrWhiteSpace($acceptedOperationId)) {{
                Invoke-TowerScoutHostHelperSelfTestRequest `
                    -Listener $listener `
                    -Profile $profile `
                    -ServerToken $serverToken `
                    -RequestToken $serverToken `
                    -Path "/operations/$acceptedOperationId"
            }}
            else {{
                [pscustomobject]@{{
                    StatusCode = 0
                    Body = [pscustomobject]@{{}}
                }}
            }}
            [pscustomobject]@{{
                accepted_status = [int] $accepted.StatusCode
                accepted_state = [string] (Get-TowerScoutHostHelperObjectValue -InputObject $accepted.Body -Name "state")
                accepted_terminal = [bool] $accepted.Body.terminal
                accepted_execution_enabled = [bool] $accepted.Body.execution_enabled
                elapsed_ms = [int] $watch.ElapsedMilliseconds
                poll_status = [int] $status.StatusCode
                poll_state = [string] (Get-TowerScoutHostHelperObjectValue -InputObject $status.Body -Name "state")
                poll_terminal = [bool] $status.Body.terminal
                poll_execution_enabled = [bool] $status.Body.execution_enabled
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if ($null -ne $listener) {{
                $listener.Stop()
            }}
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload["accepted_status"] == 202
    assert payload["accepted_terminal"] is False
    assert payload["accepted_execution_enabled"] is True
    # This is an operation-acceptance regression bound, not launcher-startup
    # or production worker timing evidence.
    assert payload["elapsed_ms"] < 4000
    assert payload["poll_status"] == 200
    assert payload["poll_state"] == "planned"
    assert payload["poll_terminal"] is False
    assert payload["poll_execution_enabled"] is True


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_fixed_worker_completes_fake_allowlisted_wrappers():
    helper_path = str(HELPER_LIB).replace("'", "''")
    helper_state_path = str(HELPER_STATE_LIB).replace("'", "''")
    worker_path = str(HELPER_WORKER_SCRIPT).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-worker-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path (Join-Path $root "scripts\\lib") -Force | Out-Null
        Copy-Item -LiteralPath '{helper_path}' -Destination (Join-Path $root "scripts\\lib\\TowerScoutHostHelper.ps1")
        Copy-Item -LiteralPath '{helper_state_path}' -Destination (Join-Path $root "scripts\\lib\\TowerScoutHostHelperState.ps1")
        Copy-Item -LiteralPath '{worker_path}' -Destination (Join-Path $root "scripts\\host-helper-worker.ps1")
        Set-Content -LiteralPath (Join-Path $root "scripts\\repair-provider-tls.cmd") -Encoding ASCII -Value "@echo off`r`nexit /b 0"
        Set-Content -LiteralPath (Join-Path $root "scripts\\stop.cmd") -Encoding ASCII -Value "@echo off`r`nexit /b 0"
        Set-Content -LiteralPath (Join-Path $root "start.bat") -Encoding ASCII -Value "@echo off`r`nset TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION>start-env.txt`r`nexit /b 0"
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile `
                -Engine "docker" `
                -Gpu "off" `
                -AppPort 5000 `
                -PackageRoot $root `
                -PackageFlavor "worker-probe" `
                -ProviderTlsRepairEnabled:$true
            Save-TowerScoutHostHelperSession -Profile $profile -Token (New-TowerScoutHostHelperToken) | Out-Null
            $request = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{
                    provider = "google"
                    confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation
                    operation_authorization = (New-TowerScoutHostHelperToken)
                }} | ConvertTo-Json -Compress)
            }}
            $accepted = New-TowerScoutProviderTlsRepairOperationPlanResponse `
                -Profile $profile `
                -Request $request `
                -ExecutionEnabled:$true
            $operationId = [string] $accepted.Body.operation_id
            $deadline = (Get-Date).AddSeconds(15)
            $poll = $null
            do {{
                Start-Sleep -Milliseconds 100
                $poll = Get-TowerScoutHostHelperOperationStatus `
                    -Profile $profile `
                    -OperationId $operationId
            }} while (-not [bool] $poll.Body.terminal -and (Get-Date) -lt $deadline)
            $activeLockPath = Get-TowerScoutHostHelperOperationLockPath -Profile $profile
            $workerIdentityPath = Get-TowerScoutHostHelperOperationWorkerPath `
                -Profile $profile `
                -OperationId $operationId
            $cleanupDeadline = (Get-Date).AddSeconds(5)
            while ((Get-Date) -lt $cleanupDeadline) {{
                $activeLock = Get-TowerScoutHostHelperOperationLock -Profile $profile
                $activeLockFileExists = Test-Path -LiteralPath $activeLockPath -PathType Leaf
                $workerIdentityFileExists = Test-Path -LiteralPath $workerIdentityPath -PathType Leaf
                if (
                    $null -eq $activeLock -and
                    -not $activeLockFileExists -and
                    -not $workerIdentityFileExists
                ) {{
                    break
                }}
                Start-Sleep -Milliseconds 100
            }}
            $activeLock = Get-TowerScoutHostHelperOperationLock -Profile $profile
            $activeLockFileExists = Test-Path -LiteralPath $activeLockPath -PathType Leaf
            $workerIdentityFileExists = Test-Path -LiteralPath $workerIdentityPath -PathType Leaf
            $statusPath = Get-TowerScoutHostHelperOperationStatusPath -Profile $profile -OperationId $operationId
            $statusAcl = Get-Acl -LiteralPath $statusPath
            [pscustomobject]@{{
                accepted_status = [int] $accepted.StatusCode
                accepted_execution_enabled = [bool] $accepted.Body.execution_enabled
                terminal_status = [int] $poll.StatusCode
                terminal_state = [string] $poll.Body.state
                terminal = [bool] $poll.Body.terminal
                active_lock_released = $null -eq $activeLock
                active_lock_file_removed = -not $activeLockFileExists
                worker_identity_file_removed = -not $workerIdentityFileExists
                status_acl_protected = [bool] $statusAcl.AreAccessRulesProtected
                retained_status_available = $null -ne (
                    Get-TowerScoutHostHelperOperationStatusRecord `
                        -Profile $profile `
                        -OperationId $operationId
                )
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            Clear-TowerScoutHostHelperSession -RootPath $root | Out-Null
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "accepted_status": 202,
        "accepted_execution_enabled": True,
        "terminal_status": 200,
        "terminal_state": "ready",
        "terminal": True,
        "active_lock_released": True,
        "active_lock_file_removed": True,
        "worker_identity_file_removed": True,
        "status_acl_protected": True,
        "retained_status_available": True,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_package_mutex_rejects_second_process():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-mutex-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $readyPath = Join-Path $root "ready"
        $childScript = @"
        . '{helper_path}'
        `$mutex = Enter-TowerScoutHostHelperPackageMutex -PackageRoot '$root'
        [System.IO.File]::WriteAllText('$readyPath', 'ready')
        Start-Sleep -Seconds 3
        `$mutex.ReleaseMutex()
        `$mutex.Dispose()
"@
        $encoded = [Convert]::ToBase64String(
            [System.Text.Encoding]::Unicode.GetBytes($childScript)
        )
        $child = Start-Process `
            -FilePath "powershell.exe" `
            -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded) `
            -WindowStyle Hidden `
            -PassThru
        try {{
            $deadline = (Get-Date).AddSeconds(5)
            while (-not (Test-Path -LiteralPath $readyPath) -and (Get-Date) -lt $deadline) {{
                Start-Sleep -Milliseconds 100
            }}
            if (-not (Test-Path -LiteralPath $readyPath)) {{
                throw "The first helper mutex process did not become ready."
            }}
            $blocked = $false
            try {{
                $second = Enter-TowerScoutHostHelperPackageMutex `
                    -PackageRoot $root `
                    -WaitMilliseconds 500
                $second.ReleaseMutex()
                $second.Dispose()
            }}
            catch {{
                $blocked = $true
            }}
            [pscustomobject]@{{
                blocked = $blocked
                first_process_alive = -not $child.HasExited
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (-not $child.HasExited) {{
                $child.WaitForExit(5000) | Out-Null
            }}
            $child.Dispose()
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "blocked": True,
        "first_process_alive": True,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_session_records_liveness_acl_and_stops_on_invalidation():
    helper_path = str(HELPER_LIB).replace("'", "''")
    helper_script = str(HELPER_SCRIPT).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-lifecycle-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $sessionId = New-TowerScoutHostHelperSessionId
        $env:TOWERSCOUT_HOST_HELPER_SESSION_KEY = New-TowerScoutHostHelperToken
        $stdoutPath = Join-Path $root "helper-stdout.txt"
        $stderrPath = Join-Path $root "helper-stderr.txt"
        $helper = Start-Process `
            -FilePath "powershell.exe" `
            -ArgumentList @(
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "{helper_script}",
                "-Engine",
                "docker",
                "-Gpu",
                "off",
                "-AppPort",
                "5000",
                "-PackageRoot",
                $root,
                "-HelperSessionId",
                $sessionId
            ) `
            -WindowStyle Hidden `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath `
            -PassThru
        try {{
            $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $root
            $sessionPath = Join-Path $stateDirectory ("session-{{0}}.json" -f $sessionId)
            $deadline = (Get-Date).AddSeconds(10)
            $metadata = $null
            while ($null -eq $metadata -and (Get-Date) -lt $deadline) {{
                if (Test-Path -LiteralPath $sessionPath) {{
                    $metadata = Get-TowerScoutHostHelperJsonDocument -Path $sessionPath
                }}
                Start-Sleep -Milliseconds 100
            }}
            if ($null -eq $metadata) {{
                $childStdout = if (Test-Path -LiteralPath $stdoutPath) {{ Get-Content -LiteralPath $stdoutPath -Raw }} else {{ "" }}
                $childStderr = if (Test-Path -LiteralPath $stderrPath) {{ Get-Content -LiteralPath $stderrPath -Raw }} else {{ "" }}
                throw "The helper session metadata did not become ready. stdout=$childStdout stderr=$childStderr"
            }}
            $tokenPath = Join-Path $stateDirectory ([string] $metadata.token_file)
            $directoryAcl = Get-Acl -LiteralPath $stateDirectory
            $sessionAcl = Get-Acl -LiteralPath $sessionPath
            $tokenAcl = Get-Acl -LiteralPath $tokenPath
            Clear-TowerScoutHostHelperSession -RootPath $root -SessionId $sessionId | Out-Null
            $helper.WaitForExit(5000) | Out-Null
            [pscustomobject]@{{
                helper_port_ready = [int] $metadata.helper_port -gt 0
                process_id_matches = [int] $metadata.process_id -eq [int] $helper.Id
                process_start_recorded = -not [string]::IsNullOrWhiteSpace([string] $metadata.process_start_time_utc)
                heartbeat_recorded = -not [string]::IsNullOrWhiteSpace([string] $metadata.last_heartbeat_utc)
                lease_recorded = -not [string]::IsNullOrWhiteSpace([string] $metadata.lease_expires_at_utc)
                directory_acl_protected = [bool] $directoryAcl.AreAccessRulesProtected
                session_acl_protected = [bool] $sessionAcl.AreAccessRulesProtected
                token_acl_protected = [bool] $tokenAcl.AreAccessRulesProtected
                helper_exited = [bool] $helper.HasExited
                session_removed = -not (Test-Path -LiteralPath $sessionPath)
                token_removed = -not (Test-Path -LiteralPath $tokenPath)
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (-not $helper.HasExited) {{
                $helper.Kill()
                $helper.WaitForExit(5000) | Out-Null
            }}
            $helper.Dispose()
            Remove-Item Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert all(payload.values()), payload


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_session_active_rejects_stale_heartbeat_and_wrong_process():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-session-liveness-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "liveness-probe"
            Save-TowerScoutHostHelperSession -Profile $profile -Token (New-TowerScoutHostHelperToken) | Out-Null
            $active = Test-TowerScoutHostHelperSessionActive -Profile $profile

            $session = Get-TowerScoutHostHelperJsonDocument -Path $profile.SessionPath
            $session.last_heartbeat_utc = (Get-Date).ToUniversalTime().AddSeconds(-30).ToString("o")
            Write-TowerScoutHostHelperJsonAtomic -Path $profile.SessionPath -Value $session
            $staleHeartbeatRejected = -not (Test-TowerScoutHostHelperSessionActive -Profile $profile)
            $listenerCanRecoverStaleHeartbeat = (
                (Test-TowerScoutHostHelperSessionActive -Profile $profile -IgnoreHeartbeatStaleness) -and
                (Update-TowerScoutHostHelperSessionHeartbeat -Profile $profile) -and
                (Test-TowerScoutHostHelperSessionActive -Profile $profile)
            )

            $session = Get-TowerScoutHostHelperJsonDocument -Path $profile.SessionPath
            $session.last_heartbeat_utc = (Get-Date).ToUniversalTime().ToString("o")
            $session.process_id = 2147483647
            Write-TowerScoutHostHelperJsonAtomic -Path $profile.SessionPath -Value $session
            $wrongProcessRejected = -not (Test-TowerScoutHostHelperSessionActive -Profile $profile)

            [pscustomobject]@{{
                active_session_accepted = [bool] $active
                stale_heartbeat_rejected = [bool] $staleHeartbeatRejected
                listener_can_recover_stale_heartbeat = [bool] $listenerCanRecoverStaleHeartbeat
                wrong_process_rejected = [bool] $wrongProcessRejected
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert all(payload.values()), payload


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_controlled_runner_is_gated_and_sanitized():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout task087 runner (&) {{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path (Join-Path $root "scripts") -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $root "scripts\\repair-provider-tls.cmd") -Encoding ASCII -Value "@echo off`r`nexit /b 0"
        Set-Content -LiteralPath (Join-Path $root "scripts\\stop.cmd") -Encoding ASCII -Value "@echo off`r`nset TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION>stop-env.txt`r`nexit /b 0"
        Set-Content -LiteralPath (Join-Path $root "start.bat") -Encoding ASCII -Value "@echo off`r`nset TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION>start-env.txt`r`nexit /b 0"
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "runner-probe" -ProviderTlsRepairEnabled:$true
            $plan = New-TowerScoutProviderTlsRepairOperationPlan -Profile $profile -Provider "google" -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
            $repairCommand = Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "repair"
            $actualRepair = Invoke-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "repair"
            $actualStop = Invoke-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "stop"
            $actualStart = Invoke-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "start"
            $controlledStopEnv = ""
            $stopEnvPath = Join-Path $root "stop-env.txt"
            if (Test-Path -LiteralPath $stopEnvPath) {{
                $controlledStopEnv = (Get-Content -LiteralPath $stopEnvPath -Raw).Trim()
            }}
            $controlledStartEnv = ""
            $startEnvPath = Join-Path $root "start-env.txt"
            if (Test-Path -LiteralPath $startEnvPath) {{
                $controlledStartEnv = (Get-Content -LiteralPath $startEnvPath -Raw).Trim()
            }}

            $badPlan = $plan | ConvertTo-Json -Depth 12 | ConvertFrom-Json
            $badPlan.InternalCommands.Start.Arguments = @("-Engine", "docker", "-Gpu", "off", "-Port", "9999", "-NoBrowser", "-TimeoutSeconds", "180")
            $badArgumentRejected = $false
            try {{
                Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $badPlan -Step "start" | Out-Null
            }}
            catch {{
                $badArgumentRejected = $true
            }}

            $badRepairScriptPlan = $plan | ConvertTo-Json -Depth 12 | ConvertFrom-Json
            $badRepairScriptPlan.InternalCommands.Repair.Script = "scripts\\repair-provider-tls-evil.cmd"
            $badRepairScriptRejected = $false
            try {{
                Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $badRepairScriptPlan -Step "repair" | Out-Null
            }}
            catch {{
                $badRepairScriptRejected = $true
            }}

            $badStopScriptPlan = $plan | ConvertTo-Json -Depth 12 | ConvertFrom-Json
            $badStopScriptPlan.InternalCommands.Stop.Script = "scripts\\stop-evil.cmd"
            $badStopScriptRejected = $false
            try {{
                Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $badStopScriptPlan -Step "stop" | Out-Null
            }}
            catch {{
                $badStopScriptRejected = $true
            }}

            $badStartScriptPlan = $plan | ConvertTo-Json -Depth 12 | ConvertFrom-Json
            $badStartScriptPlan.InternalCommands.Start.Script = "start-evil.bat"
            $badStartScriptRejected = $false
            try {{
                Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $badStartScriptPlan -Step "start" | Out-Null
            }}
            catch {{
                $badStartScriptRejected = $true
            }}

            $script:fakeCalls = @()
            $successInvoker = {{
                param($Command)
                $script:fakeCalls += [string] $Command.Step
                [pscustomobject]@{{
                    ExitCode = 0
                    TimedOut = $false
                    Stdout = "provider_key=SECRET_VALUE"
                    Stderr = "C:\\private\\certificate\\thumbprint"
                }}
            }}

            $successAuthorization = New-TowerScoutHostHelperToken
            $lock = New-TowerScoutHostHelperOperationLock -Profile $profile -Plan $plan -OperationNonce $successAuthorization
            $success = Invoke-TowerScoutProviderTlsRepairControlledExecution -Profile $profile -Plan $plan -ExecutionEnabled:$true -CommandInvoker $successInvoker
            $status = Get-TowerScoutHostHelperOperationStatus -Profile $profile -OperationId ([string] $plan.OperationId)
            $replayRequest = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{
                    provider = "google"
                    confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation
                    operation_authorization = $successAuthorization
                }} | ConvertTo-Json -Compress)
            }}
            $replay = New-TowerScoutProviderTlsRepairOperationPlanResponse -Profile $profile -Request $replayRequest

            $timeoutProfile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "runner-probe"
            $timeoutPlan = New-TowerScoutProviderTlsRepairOperationPlan -Profile $timeoutProfile -Provider "azure" -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
            New-TowerScoutHostHelperOperationLock -Profile $timeoutProfile -Plan $timeoutPlan -OperationNonce (New-TowerScoutHostHelperToken) | Out-Null
            $timeoutInvoker = {{
                param($Command)
                [pscustomobject]@{{
                    ExitCode = 1
                    TimedOut = $true
                    Stdout = "raw stdout with SECRET_VALUE"
                    Stderr = "C:\\private\\certificate\\thumbprint"
                }}
            }}
            $timeout = Invoke-TowerScoutProviderTlsRepairControlledExecution -Profile $timeoutProfile -Plan $timeoutPlan -ExecutionEnabled:$true -CommandInvoker $timeoutInvoker
            $timeoutPoll = Get-TowerScoutHostHelperOperationStatus -Profile $timeoutProfile -OperationId ([string] $timeoutPlan.OperationId)

            $publicJson = @($success, $status.Body, $timeout, $timeoutPoll.Body) | ConvertTo-Json -Depth 12 -Compress
            [pscustomobject]@{{
                repair_script = [string] $repairCommand.Script
                repair_interpreter = [System.IO.Path]::GetFileName([string] $repairCommand.InterpreterPath)
                repair_arguments = @($repairCommand.Arguments)
                actual_repair_state = [string] $actualRepair.State
                actual_stop_state = [string] $actualStop.State
                actual_start_state = [string] $actualStart.State
                controlled_stop_env = $controlledStopEnv
                controlled_start_env = $controlledStartEnv
                bad_argument_rejected = $badArgumentRejected
                bad_repair_script_rejected = $badRepairScriptRejected
                bad_stop_script_rejected = $badStopScriptRejected
                bad_start_script_rejected = $badStartScriptRejected
                success_state = [string] $success.state
                success_classification = [string] $success.classification
                success_terminal = [bool] $success.terminal
                success_step = [string] $success.current_step
                success_execution_enabled = [bool] $success.execution_enabled
                status_state = [string] $status.Body.state
                replay_status = [int] $replay.StatusCode
                replay_existing = [bool] $replay.Body.existing_operation
                replay_operation_id = [string] $replay.Body.operation_id
                calls = @($script:fakeCalls)
                timeout_state = [string] $timeout.state
                timeout_classification = [string] $timeout.classification
                timeout_terminal = [bool] $timeout.terminal
                timeout_poll_status = [int] $timeoutPoll.StatusCode
                timeout_poll_state = [string] $timeoutPoll.Body.state
                timeout_poll_classification = [string] $timeoutPoll.Body.classification
                timeout_poll_terminal = [bool] $timeoutPoll.Body.terminal
                timeout_poll_next_action = [string] $timeoutPoll.Body.next_action
                public_status_safe = -not ($publicJson -match "SECRET_VALUE|private|repair-provider-tls|scripts\\\\|start\\.bat|stop\\.cmd|certificate|thumbprint|token|secret")
            }} | ConvertTo-Json -Depth 12 -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload["repair_script"] == "scripts\\repair-provider-tls.cmd"
    assert payload["repair_interpreter"].lower() == "cmd.exe"
    assert payload["repair_arguments"] == [
        "-Provider",
        "google",
        "-Engine",
        "docker",
        "-Gpu",
        "off",
        "-Apply",
    ]
    assert payload["actual_repair_state"] == "tls_repair_completed"
    assert payload["actual_stop_state"] == "runtime_stopped"
    assert payload["actual_start_state"] == "ready"
    assert payload["controlled_stop_env"] == "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION=1"
    assert payload["controlled_start_env"] == "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION=1"
    assert payload["bad_argument_rejected"] is True
    assert payload["bad_repair_script_rejected"] is True
    assert payload["bad_stop_script_rejected"] is True
    assert payload["bad_start_script_rejected"] is True
    assert payload["success_state"] == "ready"
    assert payload["success_classification"] == "terminal_success"
    assert payload["success_terminal"] is True
    assert payload["success_step"] == "start"
    assert payload["success_execution_enabled"] is True
    assert payload["status_state"] == "ready"
    assert payload["replay_status"] == 409
    assert payload["replay_existing"] is True
    assert payload["replay_operation_id"]
    assert payload["calls"] == ["repair", "stop", "start"]
    assert payload["timeout_state"] == "operation_timeout"
    assert payload["timeout_classification"] == "terminal_timeout"
    assert payload["timeout_terminal"] is True
    assert payload["timeout_poll_status"] == 200
    assert payload["timeout_poll_state"] == "operation_timeout"
    assert payload["timeout_poll_classification"] == "terminal_timeout"
    assert payload["timeout_poll_terminal"] is True
    assert payload["timeout_poll_next_action"] == "clear_or_reauthorize_after_timeout"
    assert payload["public_status_safe"] is True


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_process_timeout_kills_wrapper_tree_before_output_read():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-timeout-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $root "sleep-child.ps1") -Encoding ASCII -Value "Start-Sleep -Seconds 20"
        Set-Content -LiteralPath (Join-Path $root "timeout-wrapper.cmd") -Encoding ASCII -Value "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%~dp0sleep-child.ps1""`r`nexit /b 0"
        try {{
            $command = [pscustomobject]@{{
                Step = "timeout_probe"
                Script = "timeout-wrapper.cmd"
                ScriptPath = (Join-Path $root "timeout-wrapper.cmd")
                Arguments = @()
                Interpreter = "cmd.exe"
                InterpreterPath = (Get-TowerScoutHostHelperBatchInterpreterPath)
                InterpreterArguments = @("/d", "/s", "/c")
                WorkingDirectory = $root
                TimeoutSeconds = 1
                EnvironmentVariables = @{{}}
            }}
            $watch = [System.Diagnostics.Stopwatch]::StartNew()
            $result = Invoke-TowerScoutHostHelperProcessCommand -Command $command
            $watch.Stop()
            [pscustomobject]@{{
                timed_out = [bool] $result.TimedOut
                exit_code = [int] $result.ExitCode
                elapsed_ms = [int] $watch.ElapsedMilliseconds
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload["timed_out"] is True
    assert payload["exit_code"] == 1
    assert payload["elapsed_ms"] < 10000


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_session_invalidation_cancels_wrapper_tree():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-cancel-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $root "sleep-child.ps1") -Encoding ASCII -Value "Start-Sleep -Seconds 20"
        Set-Content -LiteralPath (Join-Path $root "cancel-wrapper.cmd") -Encoding ASCII -Value "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%~dp0sleep-child.ps1""`r`nexit /b 0"
        $canceller = $null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "cancel-probe"
            Save-TowerScoutHostHelperSession -Profile $profile -Token (New-TowerScoutHostHelperToken) | Out-Null
            $sessionPath = [string] $profile.SessionPath
            $cancelScript = "Start-Sleep -Milliseconds 750; Remove-Item -LiteralPath '$($sessionPath.Replace("'", "''"))' -Force"
            $encodedCancel = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($cancelScript))
            $canceller = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encodedCancel) -WindowStyle Hidden -PassThru
            $command = [pscustomobject]@{{
                Step = "cancel_probe"
                Script = "cancel-wrapper.cmd"
                ScriptPath = (Join-Path $root "cancel-wrapper.cmd")
                Arguments = @()
                Interpreter = "cmd.exe"
                InterpreterPath = (Get-TowerScoutHostHelperBatchInterpreterPath)
                InterpreterArguments = @("/d", "/s", "/c")
                WorkingDirectory = $root
                TimeoutSeconds = 20
                EnvironmentVariables = @{{}}
            }}
            $watch = [System.Diagnostics.Stopwatch]::StartNew()
            $result = Invoke-TowerScoutHostHelperProcessCommand -Command $command -Profile $profile
            $watch.Stop()
            [pscustomobject]@{{
                cancelled = [bool] $result.Cancelled
                timed_out = [bool] $result.TimedOut
                exit_code = [int] $result.ExitCode
                elapsed_ms = [int] $watch.ElapsedMilliseconds
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if ($null -ne $canceller) {{
                if (-not $canceller.HasExited) {{ $canceller.WaitForExit(5000) | Out-Null }}
                $canceller.Dispose()
            }}
            Clear-TowerScoutHostHelperSession -RootPath $root | Out-Null
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload["cancelled"] is True
    assert payload["timed_out"] is False
    assert payload["exit_code"] == 1
    assert payload["elapsed_ms"] < 10000


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_marks_dead_recorded_worker_terminal():
    helper_path = str(HELPER_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-worker-{{0}}" -f (New-TowerScoutHostHelperSessionId))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "worker-probe"
            $plan = New-TowerScoutProviderTlsRepairOperationPlan -Profile $profile -Provider "google" -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
            New-TowerScoutHostHelperOperationLock -Profile $profile -Plan $plan -OperationNonce (New-TowerScoutHostHelperToken) | Out-Null
            Set-TowerScoutHostHelperOperationLockState -Profile $profile -OperationId ([string] $plan.OperationId) -State "runtime_starting" -Step "start" -ExecutionEnabled:$true | Out-Null
            $workerPath = Get-TowerScoutHostHelperOperationWorkerPath -Profile $profile -OperationId ([string] $plan.OperationId)
            Write-TowerScoutHostHelperJsonAtomic -Path $workerPath -Value ([pscustomobject]@{{
                operation_id = [string] $plan.OperationId
                process_id = 2147483647
                process_start_time_utc = (Get-Date).ToUniversalTime().ToString("o")
            }})
            $status = Get-TowerScoutHostHelperOperationStatus -Profile $profile -OperationId ([string] $plan.OperationId)
            [pscustomobject]@{{
                state = [string] $status.Body.state
                current_step = [string] $status.Body.current_step
                terminal = [bool] $status.Body.terminal
                worker_record_removed = -not (Test-Path -LiteralPath $workerPath)
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "state": "runtime_start_failed",
        "current_step": "worker_exit",
        "terminal": True,
        "worker_record_removed": True,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_json_reader_retries_under_stop_error_preference():
    state_path = str(HELPER_STATE_LIB).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        $ErrorActionPreference = 'Stop'
        . '{state_path}'
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-task087-json-{{0}}" -f ([guid]::NewGuid().ToString("N")))
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $documentPath = Join-Path $root "state.json"
        Set-Content -LiteralPath $documentPath -Encoding ASCII -Value '{{'
        try {{
            $malformed = Get-TowerScoutHostHelperJsonDocument -Path $documentPath -MaximumAttempts 2
            Set-Content -LiteralPath $documentPath -Encoding ASCII -Value '{{"state":"ready"}}'
            $document = Get-TowerScoutHostHelperJsonDocument -Path $documentPath -MaximumAttempts 2
            [pscustomobject]@{{
                malformed_returned_null = $null -eq $malformed
                parsed = $null -ne $document
                state = if ($null -ne $document) {{ [string] $document.state }} else {{ "" }}
            }} | ConvertTo-Json -Compress
        }}
        finally {{
            if (Test-Path -LiteralPath $root) {{
                Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
            }}
        }}
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "malformed_returned_null": True,
        "parsed": True,
        "state": "ready",
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_real_wrapper_contract_is_non_mutating_and_sanitized():
    helper_path = str(HELPER_LIB).replace("'", "''")
    repo_root = str(REPO_ROOT).replace("'", "''")
    script = textwrap.dedent(
        f"""
        $ProgressPreference = 'SilentlyContinue'
        . '{helper_path}'
        $root = '{repo_root}'
        $contract = Test-TowerScoutHostHelperRealWrapperContract -RootPath $root -Provider "google" -Gpu "off" -AppPort 5000
        $contractJson = $contract | ConvertTo-Json -Depth 12 -Compress
        $outputSafe = -not (
            $contractJson -match ([regex]::Escape($root)) -or
            $contractJson -match "repair-provider-tls|scripts\\\\|start\\.bat|stop\\.cmd|certificate|thumbprint|token|secret"
        )
        [pscustomobject]@{{
            state = [string] $contract.state
            provider = [string] $contract.provider
            execution_enabled = [bool] $contract.execution_enabled
            executed = [bool] $contract.executed
            runtime_engine = [string] $contract.runtime.engine
            runtime_gpu = [string] $contract.runtime.gpu
            runtime_port = [int] $contract.runtime.app_port
            step_count = [int] $contract.step_count
            step_names = @($contract.steps | ForEach-Object {{ [string] $_.step }})
            argument_counts = @($contract.steps | ForEach-Object {{ [int] $_.argument_count }})
            timeout_seconds = @($contract.steps | ForEach-Object {{ [int] $_.timeout_seconds }})
            output_safe = $outputSafe
        }} | ConvertTo-Json -Depth 12 -Compress
        """
    )

    result = _run_powershell_script(script)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(next(line for line in result.stdout.splitlines() if line))
    assert payload == {
        "state": "real_wrapper_contract_validated",
        "provider": "google",
        "execution_enabled": False,
        "executed": False,
        "runtime_engine": "docker",
        "runtime_gpu": "off",
        "runtime_port": 5000,
        "step_count": 3,
        "step_names": ["repair", "stop", "start"],
        "argument_counts": [7, 2, 9],
        "timeout_seconds": [300, 120, 240],
        "output_safe": True,
    }


@pytest.mark.skipif(os.name != "nt", reason="PowerShell host helper is Windows-only")
def test_host_helper_self_test_covers_provider_tls_operation_contract():
    powershell = _powershell_executable()
    if powershell is None:
        pytest.skip("PowerShell executable not found")

    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(HELPER_SCRIPT),
            "-SelfTest",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    scenarios = {
        scenario["name"]: scenario for scenario in payload["operation_scenarios"]
    }

    assert scenarios["provider_tls_repair_docker_plan"]["state"] == "planned"
    assert scenarios["provider_tls_repair_docker_plan"]["provider"] == "google"
    assert scenarios["provider_tls_repair_docker_plan"]["runtime"] == "docker"
    assert (
        scenarios["provider_tls_repair_podman_blocked"]["state"]
        == "unsupported_runtime"
    )
    assert (
        scenarios["provider_tls_repair_confirmation_required"]["state"]
        == "rejected_confirmation"
    )
    assert (
        scenarios["provider_tls_repair_provider_allowlist"]["state"]
        == "rejected_unknown_provider"
    )
    assert scenarios["provider_tls_repair_provider_allowlist"]["provider"] == "unknown"
    assert (
        scenarios["provider_tls_repair_single_operation_lock"]["state"]
        == "operation_busy"
    )
    assert (
        scenarios["provider_tls_repair_real_wrapper_contract"]["state"]
        == "real_wrapper_contract_validated"
    )
    assert scenarios["provider_tls_repair_real_wrapper_contract"]["executed"] is False
    assert "repair-provider-tls" not in result.stdout
    assert "scripts\\" not in result.stdout
    assert "start.bat" not in result.stdout
    assert "google;start-process" not in result.stdout.lower()
    assert "google;process-start" not in result.stdout.lower()
    assert "Start-Process" not in result.stdout
