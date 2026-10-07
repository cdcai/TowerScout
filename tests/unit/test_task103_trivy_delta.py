"""Tests for the Task-103 exact-image Trivy delta gate."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "task103_trivy_delta.py"
IMAGE_ID = "sha256:" + "1" * 64
ARTIFACT_ID = "sha256:" + "2" * 64


def _finding(
    vulnerability_id,
    package,
    severity="HIGH",
    fixed="",
    *,
    installed="1.0",
    package_id=None,
    package_class="os-pkgs",
    package_type="debian",
):
    return {
        "VulnerabilityID": vulnerability_id,
        "PkgName": package,
        "InstalledVersion": installed,
        "FixedVersion": fixed,
        "Severity": severity,
        "PkgID": package_id or f"{package}@{installed}",
        "_class": package_class,
        "_type": package_type,
    }


def _scan(
    *findings,
    artifact="towerscout:test",
    flavor="cpu",
    source_ref="candidate-sha",
    image_id=IMAGE_ID,
):
    results = []
    for package_class, package_type, target in (
        ("os-pkgs", "debian", "debian 12"),
        ("lang-pkgs", "python-pkg", "Python"),
    ):
        vulnerabilities = []
        for raw in findings:
            if raw["_class"] != package_class or raw["_type"] != package_type:
                continue
            vulnerabilities.append(
                {key: value for key, value in raw.items() if not key.startswith("_")}
            )
        results.append(
            {
                "Target": target,
                "Class": package_class,
                "Type": package_type,
                "Vulnerabilities": vulnerabilities,
            }
        )
    return {
        "SchemaVersion": 2,
        "Trivy": {"Version": "0.69.3"},
        "CreatedAt": "2026-09-24T00:00:00Z",
        "ArtifactName": artifact,
        "ArtifactID": ARTIFACT_ID,
        "Metadata": {
            "ImageID": image_id,
            "ImageConfig": {
                "config": {
                    "Labels": {
                        "org.opencontainers.image.revision": source_ref,
                        "org.towerscout.pytorch.flavor": flavor,
                    }
                }
            },
        },
        "Results": results,
    }


def _residual(finding, *, expires="2099-12-31T23:59:59Z", flavors=None):
    return {
        "vulnerability_id": finding["VulnerabilityID"],
        "package": finding["PkgName"],
        "severity": finding["Severity"],
        "installed_version": finding["InstalledVersion"],
        "package_id": finding["PkgID"],
        "package_class": finding["_class"],
        "package_type": finding["_type"],
        "applicable_publish_flavors": flavors or ["cpu", "cuda128"],
        "expires_utc": expires,
        "reason": "Bounded test residual with exact package identity.",
        "compensating_controls": ["Exact-version matching remains enforced."],
        "approved_by": "J-Schulein",
        "follow_up_task": "TASK-104",
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
    shared = (
        _finding("CVE-1", "openssl", "HIGH", "1.1"),
        _finding("CVE-2", "glibc", "CRITICAL", ""),
    )
    first = _write(tmp_path / "accepted-cpu.json", _scan(*shared))
    second = _write(
        tmp_path / "accepted-cuda.json",
        _scan(*shared, artifact="towerscout:cuda126", flavor="cuda126"),
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


def _residual_file(tmp_path, *findings):
    return _write(
        tmp_path / "accepted-residuals.json",
        {
            "schema_version": 1,
            "policy": "task103-g10-time-bounded-residuals",
            "description": "Test-only accepted residuals.",
            "findings": list(findings),
        },
    )


def _compare(tmp_path, baseline, scan, flavor="cpu", residuals=None):
    markdown = tmp_path / f"{flavor}-dispositions.md"
    delta = tmp_path / f"{flavor}-delta.json"
    report = json.loads(Path(scan).read_text(encoding="utf-8"))
    residuals = residuals or _residual_file(tmp_path)
    result = _run(
        "compare",
        "--baseline",
        baseline,
        "--accepted-residuals",
        residuals,
        "--candidate",
        scan,
        "--flavor",
        flavor,
        "--image",
        report["ArtifactName"],
        "--expected-image-id",
        report.get("Metadata", {}).get("ImageID", IMAGE_ID),
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
            _finding("CVE-1", "openssl", "HIGH", "1.1"),
            _finding("CVE-LOW", "ignored", "LOW", ""),
        ),
    )
    result, markdown, delta = _compare(tmp_path, baseline, candidate)
    assert result.returncode == 0, result.stderr
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["passed"] is True
    assert document["accepted_baseline_count"] == 1
    assert document["blocking_count"] == 0
    assert document["accepted_residual_count"] == 0
    assert document["severity_escalation_count"] == 0
    assert document["resolved_count"] == 1
    assert document["resolved_findings"][0]["vulnerability_id"] == "CVE-2"
    assert "RESOLVED in candidate" in markdown.read_text(encoding="utf-8")


def test_compare_blocks_each_unaccepted_new_high_or_critical_key(tmp_path):
    baseline = _baseline(tmp_path)
    candidate = _write(
        tmp_path / "candidate.json",
        _scan(
            _finding("CVE-1", "openssl", "HIGH", "1.1"),
            _finding("CVE-2", "glibc", "CRITICAL", ""),
            _finding("CVE-NEW", "new-package", "HIGH", "2.0"),
            flavor="cuda128",
        ),
    )
    result, markdown, delta = _compare(tmp_path, baseline, candidate, flavor="cuda128")
    assert result.returncode == 1
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["passed"] is False
    assert document["new_count"] == 1
    assert document["blocking_count"] == 1
    assert document["blocking_findings"][0]["package"] == "new-package"
    assert "BLOCK - not accepted" in markdown.read_text(encoding="utf-8")


def test_compare_accepts_exact_unexpired_residual(tmp_path):
    baseline = _baseline(tmp_path)
    urllib = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_id="urllib3@2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(urllib))
    residuals = _residual_file(tmp_path, _residual(urllib))
    result, markdown, delta = _compare(tmp_path, baseline, candidate, residuals=residuals)
    assert result.returncode == 0, result.stderr
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["passed"] is True
    assert document["accepted_baseline_count"] == 0
    assert document["new_count"] == 1
    assert document["accepted_residual_count"] == 1
    assert document["blocking_count"] == 0
    assert "ACCEPTED - time bounded" in markdown.read_text(encoding="utf-8")


@pytest.mark.parametrize("results", [None, []])
def test_compare_fails_closed_on_missing_or_empty_results(tmp_path, results):
    baseline = _baseline(tmp_path)
    report = _scan()
    if results is None:
        report.pop("Results")
    else:
        report["Results"] = results
    candidate = _write(tmp_path / "candidate.json", report)
    result, markdown, delta = _compare(tmp_path, baseline, candidate)
    assert result.returncode == 2
    assert "Results" in result.stderr
    assert not markdown.exists()
    assert not delta.exists()


def test_compare_fails_closed_when_required_scan_group_is_missing(tmp_path):
    baseline = _baseline(tmp_path)
    report = _scan()
    report["Results"] = report["Results"][:1]
    candidate = _write(tmp_path / "candidate.json", report)
    result, _, _ = _compare(tmp_path, baseline, candidate)
    assert result.returncode == 2
    assert "missing required scan groups" in result.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda report: report.update({"ArtifactName": "wrong:image"}), "artifact"),
        (lambda report: report["Metadata"].update({"ImageID": "sha256:" + "3" * 64}), "image ID"),
        (
            lambda report: report["Metadata"]["ImageConfig"]["config"]["Labels"].update(
                {"org.opencontainers.image.revision": "wrong-source"}
            ),
            "source label",
        ),
        (
            lambda report: report["Metadata"]["ImageConfig"]["config"]["Labels"].update(
                {"org.towerscout.pytorch.flavor": "cuda128"}
            ),
            "flavor label",
        ),
    ],
)
def test_compare_fails_closed_on_candidate_identity_mismatch(tmp_path, mutation, message):
    baseline = _baseline(tmp_path)
    report = _scan()
    original_artifact = report["ArtifactName"]
    original_image_id = report["Metadata"]["ImageID"]
    mutation(report)
    candidate = _write(tmp_path / "candidate.json", report)
    markdown = tmp_path / "m.md"
    delta = tmp_path / "d.json"
    result = _run(
        "compare",
        "--baseline",
        baseline,
        "--accepted-residuals",
        _residual_file(tmp_path),
        "--candidate",
        candidate,
        "--flavor",
        "cpu",
        "--image",
        original_artifact,
        "--expected-image-id",
        original_image_id,
        "--source-ref",
        "candidate-sha",
        "--markdown-out",
        markdown,
        "--json-out",
        delta,
    )
    assert result.returncode == 2
    assert message in result.stderr
    assert not markdown.exists()
    assert not delta.exists()


def test_compare_blocks_baseline_severity_escalation(tmp_path):
    baseline = _baseline(tmp_path)
    candidate = _write(
        tmp_path / "candidate.json",
        _scan(_finding("CVE-1", "openssl", "CRITICAL", "1.1")),
    )
    result, markdown, delta = _compare(tmp_path, baseline, candidate)
    assert result.returncode == 1
    document = json.loads(delta.read_text(encoding="utf-8"))
    assert document["blocking_count"] == 0
    assert document["severity_escalation_count"] == 1
    assert document["severity_escalations"][0]["baseline_severity"] == "HIGH"
    assert "BLOCK - severity escalation" in markdown.read_text(encoding="utf-8")


def test_compare_fails_closed_on_expired_residual(tmp_path):
    baseline = _baseline(tmp_path)
    urllib = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(urllib))
    residuals = _residual_file(tmp_path, _residual(urllib, expires="2026-01-01T00:00:00Z"))
    result, _, _ = _compare(tmp_path, baseline, candidate, residuals=residuals)
    assert result.returncode == 2
    assert "expired" in result.stderr


def test_compare_fails_closed_on_mismatched_or_unused_residual(tmp_path):
    baseline = _baseline(tmp_path)
    urllib = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(urllib))
    residual = _residual(urllib)
    residual["installed_version"] = "2.6.0"
    residual["package_id"] = "urllib3@2.6.0"
    result, _, _ = _compare(
        tmp_path,
        baseline,
        candidate,
        residuals=_residual_file(tmp_path, residual),
    )
    assert result.returncode == 2
    assert "did not match the candidate exactly" in result.stderr


def test_compare_fails_closed_on_duplicate_residual_key(tmp_path):
    baseline = _baseline(tmp_path)
    urllib = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(urllib))
    residual = _residual(urllib)
    result, _, _ = _compare(
        tmp_path,
        baseline,
        candidate,
        residuals=_residual_file(tmp_path, residual, copy.deepcopy(residual)),
    )
    assert result.returncode == 2
    assert "repeats finding key" in result.stderr


def test_compare_fails_closed_on_duplicate_residual_key_split_across_flavors(tmp_path):
    baseline = _baseline(tmp_path)
    urllib = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(urllib, flavor="cpu"))
    cuda_only = _residual(urllib, flavors=["cuda128"])
    cpu_only = _residual(urllib, flavors=["cpu"])
    result, _, _ = _compare(
        tmp_path,
        baseline,
        candidate,
        residuals=_residual_file(tmp_path, cuda_only, cpu_only),
    )
    assert result.returncode == 2
    assert "repeats finding key" in result.stderr


def test_residual_does_not_accept_an_additional_urllib3_version(tmp_path):
    baseline = _baseline(tmp_path)
    pip_private = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.7.0",
        package_id="urllib3@2.7.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    application_copy = _finding(
        "CVE-NEW",
        "urllib3",
        installed="2.6.0",
        package_id="urllib3@2.6.0",
        package_class="lang-pkgs",
        package_type="python-pkg",
    )
    candidate = _write(tmp_path / "candidate.json", _scan(pip_private, application_copy))
    result, _, _ = _compare(
        tmp_path,
        baseline,
        candidate,
        residuals=_residual_file(tmp_path, _residual(pip_private)),
    )
    assert result.returncode == 2
    assert "did not match the candidate exactly" in result.stderr


def test_compare_fails_closed_on_unknown_baseline_field(tmp_path):
    baseline = _baseline(tmp_path)
    document = json.loads(baseline.read_text(encoding="utf-8"))
    document["expires_utc"] = "2099-01-01T00:00:00Z"
    _write(baseline, document)
    candidate = _write(tmp_path / "candidate.json", _scan())
    result, markdown, delta = _compare(tmp_path, baseline, candidate)
    assert result.returncode == 2
    assert "unknown fields" in result.stderr
    assert not markdown.exists()
    assert not delta.exists()


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
    candidate = _scan(_finding("CVE-1", "openssl", "HIGH", "1.1"))
    candidate["Trivy"]["Version"] = "0.70.0"
    scan = _write(tmp_path / "candidate.json", candidate)
    result, markdown, delta = _compare(tmp_path, baseline, scan)
    assert result.returncode == 2
    assert "does not match baseline" in result.stderr
    assert not markdown.exists()
    assert not delta.exists()
