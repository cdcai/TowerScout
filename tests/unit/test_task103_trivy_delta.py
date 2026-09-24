"""Tests for the Task-103 exact-image Trivy delta gate."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "task103_trivy_delta.py"


def _scan(*findings, artifact="towerscout:test", flavor="cpu"):
    return {
        "SchemaVersion": 2,
        "Trivy": {"Version": "0.69.3"},
        "CreatedAt": "2026-09-24T00:00:00Z",
        "ArtifactName": artifact,
        "ArtifactID": "sha256:artifact",
        "Metadata": {
            "ImageID": "sha256:image",
            "ImageConfig": {
                "config": {
                    "Labels": {
                        "org.opencontainers.image.revision": "accepted-main",
                        "org.towerscout.pytorch.flavor": flavor,
                    }
                }
            },
        },
        "Results": [
            {
                "Target": "Debian 12",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": vulnerability_id,
                        "PkgName": package,
                        "InstalledVersion": "1.0",
                        "FixedVersion": fixed,
                        "Severity": severity,
                    }
                    for vulnerability_id, package, severity, fixed in findings
                ],
            }
        ],
    }


def _write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        check=False,
        capture_output=True,
        text=True,
    )


def _baseline(tmp_path):
    first = _write(
        tmp_path / "accepted-cpu.json",
        _scan(
            ("CVE-1", "openssl", "HIGH", "1.1"),
            ("CVE-2", "glibc", "CRITICAL", ""),
        ),
    )
    second = _write(
        tmp_path / "accepted-cuda.json",
        _scan(
            ("CVE-1", "openssl", "HIGH", "1.1"),
            ("CVE-2", "glibc", "CRITICAL", ""),
            artifact="towerscout:cuda126",
            flavor="cuda126",
        ),
    )
    baseline = tmp_path / "baseline.json"
    result = _run(
        "create-baseline",
        "--scan",
        first,
        "--scan",
        second,
        "--database-updated-at",
        "2026-09-24T00:00:00Z",
        "--created-utc",
        "2026-09-24T00:00:01Z",
        "--out",
        baseline,
    )
    assert result.returncode == 0, result.stderr
    return baseline


def _compare(tmp_path, baseline, scan, flavor="cpu"):
    markdown = tmp_path / f"{flavor}-dispositions.md"
    delta = tmp_path / f"{flavor}-delta.json"
    result = _run(
        "compare",
        "--baseline",
        baseline,
        "--candidate",
        scan,
        "--flavor",
        flavor,
        "--image",
        f"example@sha256:{flavor}",
        "--source-ref",
        "candidate-sha",
        "--markdown-out",
        markdown,
        "--json-out",
        delta,
    )
    return result, markdown, delta


def test_create_baseline_records_matching_scan_sources(tmp_path):
    baseline = _baseline(tmp_path)
    document = json.loads(baseline.read_text(encoding="utf-8"))

    assert document["policy"] == "task103-g10-no-new-high-critical"
    assert document["accepted_stage"] == "A"
    assert document["finding_count"] == 2
    assert len(document["sources"]) == 2
    assert document["applicable_publish_flavors"] == ["cpu", "cuda128"]
    assert all(source["raw_report_sha256"] for source in document["sources"])


def test_compare_passes_unchanged_and_records_resolved_delta(tmp_path):
    baseline = _baseline(tmp_path)
    candidate = _write(
        tmp_path / "candidate.json",
        _scan(
            ("CVE-1", "openssl", "HIGH", "1.1"),
            ("CVE-LOW", "ignored", "LOW", ""),
        ),
    )

    result, markdown, delta = _compare(tmp_path, baseline, candidate)

    assert result.returncode == 0, result.stderr
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["passed"] is True
    assert document["new_count"] == 0
    assert document["resolved_count"] == 1
    assert document["resolved_findings"][0]["vulnerability_id"] == "CVE-2"
    assert "RESOLVED in candidate" in markdown.read_text(encoding="utf-8")


def test_compare_blocks_each_new_high_or_critical_key(tmp_path):
    baseline = _baseline(tmp_path)
    candidate = _write(
        tmp_path / "candidate.json",
        _scan(
            ("CVE-1", "openssl", "HIGH", "1.1"),
            ("CVE-2", "glibc", "CRITICAL", ""),
            ("CVE-NEW", "new-package", "HIGH", "2.0"),
        ),
    )

    result, markdown, delta = _compare(tmp_path, baseline, candidate, flavor="cuda128")

    assert result.returncode == 1
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["passed"] is False
    assert document["new_count"] == 1
    assert document["new_findings"][0]["package"] == "new-package"
    assert "BLOCK - new versus committed baseline" in markdown.read_text(
        encoding="utf-8"
    )


def test_compare_fails_closed_on_tampered_baseline_count(tmp_path):
    baseline = _baseline(tmp_path)
    document = json.loads(baseline.read_text(encoding="utf-8"))
    document["finding_count"] = 999
    _write(baseline, document)
    candidate = _write(tmp_path / "candidate.json", _scan())

    result, markdown, delta = _compare(tmp_path, baseline, candidate)

    assert result.returncode == 2
    assert "finding_count does not match" in result.stderr
    assert not markdown.exists()
    assert not delta.exists()


def test_compare_fails_closed_on_scanner_version_mismatch(tmp_path):
    baseline = _baseline(tmp_path)
    candidate = _scan(("CVE-1", "openssl", "HIGH", "1.1"))
    candidate["Trivy"]["Version"] = "0.70.0"
    scan = _write(tmp_path / "candidate.json", candidate)

    result, markdown, delta = _compare(tmp_path, baseline, scan)

    assert result.returncode == 2
    assert "does not match baseline" in result.stderr
    assert not markdown.exists()
    assert not delta.exists()
