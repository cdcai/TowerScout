"""Execute only the CA selector with synthetic chains; never inspect live stores or network."""
import json
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('store,count', [('',0), ('Cert:\\LocalMachine\\CA',0), ('Cert:\\CurrentUser\\CA',0), ('Cert:\\LocalMachine\\Root',1), ('Cert:\\CurrentUser\\Root',1)])
def test_automatic_tls_selection_requires_an_existing_trusted_root(store,count):
    powershell=shutil.which('powershell.exe')
    if not powershell:
        pytest.skip('Windows PowerShell is required')
    command=f'''
    $ErrorActionPreference = 'Stop'
    $errors = $null
    $tokens = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile('{ROOT / 'scripts/repair-provider-tls.ps1'}', [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {{ throw 'Script parse failed' }}
    foreach ($name in @('Get-TowerScoutStoreScore','Select-TowerScoutTlsCaCandidate')) {{
        $definition = $ast.FindAll({{ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name }}, $true) | Select-Object -First 1
        . ([ScriptBlock]::Create($definition.Extent.Text))
    }}
    function Test-TowerScoutCertificateIsCa {{ param($Certificate) return $true }}
    function Test-TowerScoutCertificateCanSign {{ param($Certificate) return $true }}
    function Get-TowerScoutCertificateStoreMatches {{
        param($Certificate)
        if ('{store}') {{ [PSCustomObject]@{{StorePath='{store}'}} }}
    }}
    $cert = [PSCustomObject]@{{Thumbprint='SYNTHETIC';Subject='Synthetic';Issuer='Synthetic';NotAfter=(Get-Date).AddDays(1)}}
    $selected = @(Select-TowerScoutTlsCaCandidate -ChainElements @([PSCustomObject]@{{Index=1;Certificate=$cert}}))
    @{{selected=$selected.Count}} | ConvertTo-Json -Compress
    '''
    result=subprocess.run([powershell,'-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['selected']==count
