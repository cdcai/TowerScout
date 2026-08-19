"""Task-098/101 CI security-ratchet contracts."""

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
TASK_087_PUPPETEER_WORKFLOW = (
    REPO_ROOT / ".github" / "workflows" / "task-087-frontend-puppeteer.yml"
)
DOCKERFILE = REPO_ROOT / "Dockerfile"
CHECKOUT_ACTION = (
    "actions/checkout@"
    "93cb6efe18208431cddfb8368fd83d5badbf9bfd"
)
TRIVY_ACTION = (
    "aquasecurity/trivy-action@"
    "57a97c7e7821a5776cebc9bb87c984fa69cba8f1"
)


def _workflow() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


def _task_087_puppeteer_workflow() -> str:
    return TASK_087_PUPPETEER_WORKFLOW.read_text(encoding="utf-8")


def _dockerfile() -> str:
    return DOCKERFILE.read_text(encoding="utf-8")


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


def test_task_101_main_ci_uses_node_22_and_commonjs_smoke() -> None:
    workflow = _workflow()

    assert "node-version: '22'" in workflow
    assert "node-version: '18'" not in workflow
    assert "Verify CommonJS Puppeteer compatibility" in workflow
    assert "require('puppeteer')" in workflow
    assert "typeof puppeteer.launch !== 'function'" in workflow


def test_task_101_docker_frontend_uses_node_22() -> None:
    dockerfile = _dockerfile()

    assert "FROM node:22-bookworm-slim AS frontend" in dockerfile
    assert "FROM node:18" not in dockerfile


def test_task_101_pr_ci_builds_docker_frontend_stage_as_blocking_job() -> None:
    workflow = yaml.safe_load(_workflow())
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["pull_request"]["branches"] == ["main"]

    job = workflow["jobs"]["frontend-container-build"]

    assert job["name"] == "Docker frontend stage"
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] == 15
    assert "if" not in job
    assert "continue-on-error" not in job

    action_steps = [step for step in job["steps"] if "uses" in step]
    assert action_steps == [{"uses": CHECKOUT_ACTION}]

    build_steps = [
        step
        for step in job["steps"]
        if step.get("name") == "Build Docker frontend stage"
    ]
    assert len(build_steps) == 1
    build_step = build_steps[0]
    assert (
        build_step["run"]
        == "docker build --target frontend --tag towerscout-frontend:test ."
    )
    assert "if" not in build_step
    assert "continue-on-error" not in build_step


def test_task_087_puppeteer_uses_supported_node_and_pinned_playwright() -> None:
    workflow = _task_087_puppeteer_workflow()

    assert workflow.count("node-version: '22'") == 2
    assert workflow.count("PUPPETEER_SKIP_DOWNLOAD: 'true'") == 2
    assert workflow.count(
        "npx -y playwright@1.62.0 install --with-deps chromium"
    ) == 2
    assert "node-version: '18'" not in workflow
    assert "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD" not in workflow
    assert "playwright@latest" not in workflow
