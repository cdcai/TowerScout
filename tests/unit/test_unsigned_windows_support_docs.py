from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


PUBLIC_UNSIGNED_DOCS = (
    "README.md",
    "docs/quick-start.md",
    "docs/quick-start.html",
    "docs/package-guide.md",
    "docs/user-guide.md",
    "docs/user-guide.html",
    "docs/project-overview.md",
    "docs/project-overview.html",
    "docs/docker-cpu-user-guide.md",
    "docs/docker-gpu-user-guide.md",
    "docs/podman-cpu-user-guide.md",
    "docs/podman-gpu-user-guide.md",
    "docs/support/oci-quick-start.md",
    "docs/support/oci-runtime-contract.md",
    "docs/release/release-asset-bundle-contract.md",
)


AGENT_DECISION_DOCS = (
    "AGENTS.md",
    ".agent_work/README.md",
    ".agent_work/current-tasks.md",
    ".agent_work/requirements.md",
    ".agent_work/design.md",
    ".agent_work/task-backlog.md",
    ".agent_work/tasks/active/TASK-092-documentation-currentness.md",
    ".agents/skills/towerscout-release-candidate-gate/SKILL.md",
    ".agents/skills/towerscout-container-windows-runtime/SKILL.md",
    ".agents/skills/towerscout-end-user-docs-check/SKILL.md",
)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_current_public_docs_disclose_unsigned_windows_boundary():
    for relative_path in PUBLIC_UNSIGNED_DOCS:
        text = _read(relative_path)
        assert "unsigned" in text, relative_path
        assert "execution-policy" in text or "execution policy" in text, relative_path
        assert "set-executionpolicy" not in text, relative_path


def test_primary_install_docs_require_authoritative_hash_before_extraction():
    for relative_path in (
        "README.md",
        "docs/quick-start.md",
        "docs/quick-start.html",
        "docs/package-guide.md",
        "docs/project-overview.md",
        "docs/project-overview.html",
    ):
        text = _read(relative_path)
        assert "authoritative release" in text, relative_path
        assert "before extract" in text, relative_path


def test_agent_sources_point_to_adr_023_or_state_its_boundary():
    for relative_path in AGENT_DECISION_DOCS:
        text = _read(relative_path)
        assert "adr-023" in text or "unsigned" in text, relative_path


def test_adr_023_is_accepted_and_keeps_managed_endpoint_claim_narrow():
    text = _read(
        ".agent_work/decisions/023-unsigned-windows-package-support-boundary.md"
    )
    assert "**status**: accepted" in text
    assert "without authenticode" in text
    assert "out of scope, not" in text
    assert "browser-downloaded" in text
