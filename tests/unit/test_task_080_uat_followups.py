"""TASK-080 pre-UAT follow-up documentation contracts."""

import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[2]
UAT_GUIDE = (
    REPO_ROOT
    / ".agent_work"
    / "user-testing"
    / "instructions"
    / "TowerScout_V1_RC1_UAT_User_Guide.docx"
)
ISSUE_FORM = (
    REPO_ROOT
    / ".agent_work"
    / "user-testing"
    / "instructions"
    / "TESTER-ISSUE-REPORT-CHECKLIST.txt"
)
QUICK_START = REPO_ROOT / "docs" / "quick-start.md"


def _docx_text(path: Path) -> str:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as package:
        root = ET.fromstring(package.read("word/document.xml"))
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n".join(paragraphs)


def _compact(text: str) -> str:
    return " ".join(text.split())


def test_word_uat_guide_contains_pre_uat_followup_sections():
    text = _docx_text(UAT_GUIDE)
    lower_text = text.lower()
    compact = _compact(text)

    assert "Docker Desktop is open and running" in text
    assert "6. Optional Support-Assigned Tracks" in text
    assert "1. What You Are Testing" in text
    assert "Appendix A. Command Reference" in text
    assert ".\\setup-towerscout.cmd -Engine docker -Gpu auto" in compact
    assert ".\\setup-towerscout.cmd -Engine podman -Gpu on" in compact
    assert ".\\scripts\\status.cmd -Engine podman" in compact
    assert "replace -Engine docker with -Engine podman" in text
    assert "selected_device=cuda" in text
    assert "What setup_required means" in text
    assert "Short issue report form" in text
    assert "Command or button" in text
    assert "Provider setup and imported assets are stored in named volumes" in text
    assert "raw provider responses" in lower_text
    assert "API keys" in text
    assert "TLS inspection certificate" in text
    assert "scripts\\import-tls-ca.cmd" in text
    assert "TLS CA import" in text and "only if support asks" in text


def test_quick_start_mirrors_command_appendix_and_stale_session_note():
    text = QUICK_START.read_text(encoding="utf-8")
    compact = _compact(text)

    assert "## Appendix: Command Reference" in text
    assert "Docker Desktop is open and running" in text
    assert "Docker GPU setup" in text
    assert ".\\setup-towerscout.cmd -Engine docker -Gpu auto" in text
    assert ".\\start.bat -Engine podman -Gpu off" in text
    assert ".\\scripts\\logs.cmd -Engine podman -Tail 200" in text
    assert "-SessionMaxHours 24" in text
    assert "older than 12 hours" in compact
    assert "keeps named volumes by default" in compact
    assert "CERTIFICATE_VERIFY_FAILED" in text
    assert "TLS inspection certificate" in text
    assert "updates the local `.env`" in text
    assert ".\\scripts\\import-tls-ca.cmd -Engine docker" in text
    assert "Do not send provider keys, full `.env` files" in text


def test_tester_issue_form_is_short_safe_and_email_friendly():
    text = ISSUE_FORM.read_text(encoding="utf-8")
    compact = _compact(text)

    assert "Paste the completed form into email or Teams" in compact
    assert "Guide and step number" in text
    assert "What you clicked or the exact command you ran" in text
    assert "Exact error text" in text
    assert "Engine used" in text
    assert "Did Setup Wizard save the provider configuration?" in text
    assert "Estimated tile count" in text
    assert "Do not send these unless support asks" in text
    assert "API keys or full `.env` files" in text
    assert "Raw logs" in text or "raw logs" in text
    assert "browser network traces" in text
