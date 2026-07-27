"""Task-098 CI security-ratchet contracts."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
TASK_087_PUPPETEER_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "task-087-frontend-puppeteer.yml"
)
TRIVY_ACTION = (
    "aquasecurity/trivy-action@"
    "57a97c7e7821a5776cebc9bb87c984fa69cba8f1"
)


def _workflow() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


def _task_087_puppeteer_workflow() -> str:
    return TASK_087_PUPPETEER_WORKFLOW.read_text(encoding="utf-8")


def test_trivy_action_and_binary_are_pinned() -> None:
    workflow = _workflow()

    assert workflow.count(TRIVY_ACTION) == 2
    assert workflow.count("version: 'v0.69.3'") == 2
    assert "aquasecurity/trivy-action@master" not in workflow


def test_all_severity_sarif_path_remains_uploadable() -> None:
    workflow = _workflow()

    assert "format: 'sarif'" in workflow
    assert "output: 'trivy-results.sarif'" in workflow
    assert "exit-code: '0'" in workflow
    assert "if: always()" in workflow
    assert "sarif_file: 'trivy-results.sarif'" in workflow


def test_critical_high_gate_is_separate_and_does_not_ignore_unfixed() -> None:
    workflow = _workflow()

    gate = workflow.split(
        "- name: Evaluate critical and high vulnerability gate", maxsplit=1
    )[1].split(
        "- name: Upload Trivy scan results to GitHub Security tab", maxsplit=1
    )[0]
    assert "severity: 'CRITICAL,HIGH'" in gate
    assert "exit-code: '1'" in gate
    assert "ignore-unfixed: 'false'" in gate
    assert "continue-on-error" not in gate


def test_weekly_scan_is_scheduled() -> None:
    workflow = _workflow()

    assert "schedule:" in workflow
    assert "cron: '23 9 * * 1'" in workflow


def test_frontend_high_severity_audit_is_blocking() -> None:
    workflow = _workflow()

    audit = workflow.split(
        "- name: Audit frontend dependencies for high severity vulnerabilities",
        maxsplit=1,
    )[1].split("- name: Rebuild frontend bundle", maxsplit=1)[0]
    assert "npm audit --audit-level=high" in audit
    assert "continue-on-error" not in audit


def test_task_087_puppeteer_uses_supported_node_and_pinned_playwright() -> None:
    workflow = _task_087_puppeteer_workflow()

    assert workflow.count("node-version: '22'") == 2
    assert workflow.count(
        "npx -y playwright@1.62.0 install --with-deps chromium"
    ) == 2
    assert "node-version: '18'" not in workflow
    assert "playwright@latest" not in workflow
