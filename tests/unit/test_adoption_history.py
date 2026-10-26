"""Exercise history exclusion against actual disposable Git repositories."""

import importlib.util
from pathlib import Path
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "check_adoption_history", ROOT / "scripts/check_adoption_history.py"
)
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    git("init", "-q")
    git("config", "user.name", "Synthetic test")
    git("config", "user.email", "test@example.invalid")
    git("commit", "--allow-empty", "-qm", "Clean base")
    return tmp_path


def test_clean_full_history_passes(repo):
    history.main()


@pytest.mark.parametrize('name', ['CONTENTS.TXT', '.agent_work/private.md', '.AGENT_WORK/private.md'])
def test_private_archive_and_case_variant_history_are_blocked(repo, name):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('synthetic fixture', encoding='utf-8')
    git('add', name)
    git('commit', '-qm', 'Synthetic excluded content')
    with pytest.raises(ValueError):
        history.main()


def test_deleted_file_still_fails(repo):
    (repo / "contents.txt").write_text("synthetic fixture", encoding="utf-8")
    git("add", "contents.txt")
    git("commit", "-qm", "Add fixture")
    git("rm", "contents.txt")
    git("commit", "-qm", "Delete fixture")
    with pytest.raises(ValueError, match="contents.txt"):
        history.main()


@pytest.mark.parametrize('name', ['CONTENTS.TXT', '.agent_work/private.md', '.AGENT_WORK/private.md'])
def test_excluded_path_reusing_public_blob_then_deleted_is_blocked(repo, name):
    # rev-list --objects emits each object once, under only one of its paths.
    (repo / 'public.txt').write_text('same synthetic bytes', encoding='utf-8')
    git('add', 'public.txt')
    git('commit', '-qm', 'Public fixture')
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('same synthetic bytes', encoding='utf-8')
    git('add', name)
    git('commit', '-qm', 'Excluded path reuses a known public blob')
    git('rm', name)
    git('commit', '-qm', 'Remove excluded path')
    with pytest.raises(ValueError):
        history.main()


def test_excluded_blob_under_another_name_fails(repo, monkeypatch):
    (repo / "renamed.txt").write_text("synthetic fixture", encoding="utf-8")
    git("add", "renamed.txt")
    git("commit", "-qm", "Renamed fixture")
    monkeypatch.setattr(history, "EXCLUDED_BLOB", git("rev-parse", "HEAD:renamed.txt"))
    with pytest.raises(ValueError, match="blob"):
        history.main()


def test_shallow_history_fails(repo, tmp_path_factory, monkeypatch):
    clone = tmp_path_factory.mktemp("history-clone") / "repo"
    git("clone", "-q", "--depth=1", repo.as_uri(), str(clone))
    monkeypatch.chdir(clone)
    with pytest.raises(ValueError, match="Full Git history"):
        history.main()


def test_official_required_job_checks_full_candidate_history():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    job = workflow["jobs"]["frontend-test"]
    assert not job.get("continue-on-error", False)
    steps = job["steps"]
    assert steps[0]["with"]["fetch-depth"] == 0
    check = next(
        s for s in steps if s.get("name") == "Verify adoption history exclusion"
    )
    assert check["if"] == "github.repository == 'cdcai/TowerScout'"
    assert check["run"] == "python3 scripts/check_adoption_history.py"
    assert not check.get("continue-on-error", False)
