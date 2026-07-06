import base64
import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutHostHelper.ps1"
HELPER_SCRIPT = REPO_ROOT / "scripts" / "host-helper.ps1"
STOP_SCRIPT = REPO_ROOT / "scripts" / "stop.ps1"


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
    assert "provider_tls_repair = $false" in script
    assert "$script:TowerScoutHostHelperExecutionEnabledByDefault = $false" in script
    assert "function Resolve-TowerScoutHostHelperControlledCommand" in script
    assert "function Invoke-TowerScoutHostHelperControlledCommand" in script
    assert "function Invoke-TowerScoutProviderTlsRepairControlledExecution" in script
    assert "function Test-TowerScoutHostHelperRealWrapperContract" in script
    assert "function Get-TowerScoutHostHelperBatchInterpreterPath" in script
    assert 'Interpreter = "cmd.exe"' in script
    assert '"real_wrapper_contract_validated"' in script
    assert "executed = $false" in script
    assert "function Get-TowerScoutHostHelperAllowedMethodsForPath" in script
    assert '"Access-Control-Allow-Methods: $AccessControlAllowMethods"' in script
    assert 'return "GET, OPTIONS"' in script
    assert 'return "POST, OPTIONS"' in script
    assert "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION" in script
    assert "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION" in stop_script
    assert "Clear-TowerScoutHostHelperSession" in stop_script


def test_host_helper_provider_tls_repair_operation_api_is_bounded_and_non_mutating():
    script = HELPER_LIB.read_text(encoding="utf-8")

    assert "$script:TowerScoutHostHelperMaxBodyBytes = 4096" in script
    assert (
        '$script:TowerScoutHostHelperOperationAuthorizationPattern = '
        '"^[A-Za-z0-9_-]{32,128}$"'
    ) in script
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
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "api-probe"
            $authorization = New-TowerScoutHostHelperToken
            $request = [pscustomobject]@{{
                Headers = @{{ "content-type" = "application/json" }}
                BodyText = (@{{ provider = "google"; confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation; operation_authorization = $authorization }} | ConvertTo-Json -Compress)
            }}
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
                planned_status = $planned.StatusCode
                planned_state = [string] $planned.Body.state
                execution_enabled = [bool] $planned.Body.execution_enabled
                status_poll = $status.StatusCode
                same_authorization = $same.StatusCode
                same_existing = [bool] $same.Body.existing_operation
                different_authorization = $busy.StatusCode
                different_state = [string] $busy.Body.state
                unexpected_field = $unexpected.StatusCode
                unexpected_state = [string] $unexpected.Body.state
                execution_enabled_field = $executionEnabledRejected.StatusCode
                execution_enabled_field_state = [string] $executionEnabledRejected.Body.state
                bad_authorization = $badAuthorization.StatusCode
                bad_authorization_state = [string] $badAuthorization.Body.state
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
        "planned_status": 202,
        "planned_state": "planned",
        "execution_enabled": False,
        "status_poll": 200,
        "same_authorization": 202,
        "same_existing": True,
        "different_authorization": 409,
        "different_state": "operation_busy",
        "unexpected_field": 400,
        "unexpected_state": "rejected_unexpected_field",
        "execution_enabled_field": 400,
        "execution_enabled_field_state": "rejected_unexpected_field",
        "bad_authorization": 400,
        "bad_authorization_state": "rejected_operation_authorization",
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
        Set-Content -LiteralPath (Join-Path $root "start.bat") -Encoding ASCII -Value "@echo off`r`nexit /b 0"
        try {{
            $profile = New-TowerScoutHostHelperRuntimeProfile -Engine "docker" -Gpu "off" -AppPort 5000 -PackageRoot $root -PackageFlavor "runner-probe"
            $plan = New-TowerScoutProviderTlsRepairOperationPlan -Profile $profile -Provider "google" -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
            $repairCommand = Resolve-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "repair"
            $actualRepair = Invoke-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "repair"
            $actualStop = Invoke-TowerScoutHostHelperControlledCommand -Profile $profile -Plan $plan -Step "stop"
            $controlledStopEnv = ""
            $stopEnvPath = Join-Path $root "stop-env.txt"
            if (Test-Path -LiteralPath $stopEnvPath) {{
                $controlledStopEnv = (Get-Content -LiteralPath $stopEnvPath -Raw).Trim()
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

            $lock = New-TowerScoutHostHelperOperationLock -Profile $profile -Plan $plan -OperationNonce (New-TowerScoutHostHelperToken)
            $success = Invoke-TowerScoutProviderTlsRepairControlledExecution -Profile $profile -Plan $plan -ExecutionEnabled:$true -CommandInvoker $successInvoker
            $status = Get-TowerScoutHostHelperOperationStatus -Profile $profile -OperationId ([string] $plan.OperationId)

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
                controlled_stop_env = $controlledStopEnv
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
                calls = @($script:fakeCalls)
                timeout_state = [string] $timeout.state
                timeout_classification = [string] $timeout.classification
                timeout_terminal = [bool] $timeout.terminal
                timeout_poll_status = [int] $timeoutPoll.StatusCode
                timeout_poll_state = [string] $timeoutPoll.Body.state
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
    assert payload["controlled_stop_env"] == "TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION=1"
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
    assert payload["calls"] == ["repair", "stop", "start"]
    assert payload["timeout_state"] == "operation_timeout"
    assert payload["timeout_classification"] == "terminal_timeout"
    assert payload["timeout_terminal"] is True
    assert payload["timeout_poll_status"] == 410
    assert payload["timeout_poll_state"] == "operation_expired"
    assert payload["public_status_safe"] is True


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
        "timeout_seconds": [300, 120, 180],
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
