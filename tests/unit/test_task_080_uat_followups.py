"""Public installation and safe issue-report contracts."""
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUE_FORM = REPO_ROOT / "docs/support/issue-report-form.txt"
QUICK_START = REPO_ROOT / "docs/quick-start.md"
def _compact(text):
    return " ".join(text.split())

def test_current_quick_start_keeps_user_commands_and_moves_advanced_tls_to_it():
    text = QUICK_START.read_text(encoding="utf-8")
    compact = _compact(text)

    assert "## The Three Independent Choices" in text
    assert "Docker Desktop or Podman Desktop" in text
    assert "CPU or a compatible NVIDIA GPU" in text
    assert "Google Maps or Azure Maps" in text
    assert ".\\setup-towerscout.cmd -Engine docker -Gpu off" in text
    assert ".\\setup-towerscout.cmd -Engine podman -Gpu on" in text
    assert ".\\start.bat -Engine podman -Gpu off" in text
    assert ".\\scripts\\logs.cmd -Engine docker -Tail 200" in text
    assert "For Podman, replace `docker` with `podman`" in text
    assert "Save Your Setup Record" in text
    assert "Normal stop/start and reboot preserve" in compact
    assert "named volumes" in compact
    assert "Local IT Administrator Guide" in text
    assert "Do not disable TLS verification" in compact
    assert ".\\scripts\\repair-provider-tls.cmd" not in text
    assert "support-assigned" not in text.lower()


def test_tester_issue_form_is_short_safe_and_uses_public_support_route():
    text = ISSUE_FORM.read_text(encoding="utf-8")
    compact = _compact(text)

    assert "Submit the sanitized form at https://github.com/cdcai/TowerScout/issues" in compact
    assert "Guide and step number" in text
    assert "What you clicked or the command structure" in text
    assert "Sanitized error category/message" in text
    assert "Engine used" in text
    assert "Did Setup Wizard save the provider configuration?" in text
    assert "Estimated tile count" in text
    assert "PUBLIC issue tracker" in text
    assert "Public reproducible fixture identifier" in text
    assert "Search text or location used:" not in text
    assert "Shape and radius or boundary:" not in text
    assert "logs.cmd" not in text
    assert "private transfer method first" in compact
    assert "not assumed enabled" in text
    assert "API keys or full `.env` files" in text
    assert "Raw logs" in text or "raw logs" in text
    assert "browser network traces" in text
