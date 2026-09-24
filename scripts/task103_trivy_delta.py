#!/usr/bin/env python3
"""Create and enforce the TASK-103 Trivy HIGH/CRITICAL delta baseline.

The publish workflow scans the exact pushed digest.  This helper compares the
result with a committed, normalized baseline using the same key as the
TASK-103 G10 comparator: ``(VulnerabilityID, PkgName)``.  A candidate passes
only when it introduces no new HIGH or CRITICAL key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

BLOCKING_SEVERITIES = frozenset({"HIGH", "CRITICAL"})
SEVERITY_ORDER = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
POLICY = "task103-g10-no-new-high-critical"


class InputError(Exception):
    """A malformed or inconsistent scan/baseline input."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{label} {path} must contain a JSON object")
    return value


def _write_text(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label} must be a non-empty string")
    return value.strip()


def _string_values(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, str):
        return []
    return [value] if value else []


def _extract_findings(
    report: dict[str, Any], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    results = report.get("Results") or []
    if not isinstance(results, list):
        raise InputError(f"{label}.Results must be a list")
    findings: dict[tuple[str, str], dict[str, Any]] = {}
    for result_index, result in enumerate(results):
        if not isinstance(result, dict):
            raise InputError(f"{label}.Results[{result_index}] must be an object")
        target = str(result.get("Target") or "unknown")
        vulnerabilities = result.get("Vulnerabilities") or []
        if not isinstance(vulnerabilities, list):
            raise InputError(
                f"{label}.Results[{result_index}].Vulnerabilities must be a list or null"
            )
        for vuln_index, vulnerability in enumerate(vulnerabilities):
            if not isinstance(vulnerability, dict):
                raise InputError(
                    f"{label}.Results[{result_index}].Vulnerabilities[{vuln_index}] must be an object"
                )
            severity = str(vulnerability.get("Severity") or "UNKNOWN").upper()
            if severity not in BLOCKING_SEVERITIES:
                continue
            vulnerability_id = _required_text(
                vulnerability.get("VulnerabilityID"),
                f"{label}.Results[{result_index}].Vulnerabilities[{vuln_index}].VulnerabilityID",
            )
            package = _required_text(
                vulnerability.get("PkgName"),
                f"{label}.Results[{result_index}].Vulnerabilities[{vuln_index}].PkgName",
            )
            key = (vulnerability_id, package)
            entry = findings.setdefault(
                key,
                {
                    "vulnerability_id": vulnerability_id,
                    "package": package,
                    "severity": severity,
                    "targets": set(),
                    "installed_versions": set(),
                    "fixed_versions": set(),
                },
            )
            if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(
                entry["severity"], 0
            ):
                entry["severity"] = severity
            entry["targets"].add(target)
            entry["installed_versions"].update(
                _string_values(vulnerability.get("InstalledVersion"))
            )
            entry["fixed_versions"].update(
                _string_values(vulnerability.get("FixedVersion"))
            )
    return findings


def _serializable_finding(finding: dict[str, Any], *, details: bool) -> dict[str, Any]:
    value = {
        "vulnerability_id": finding["vulnerability_id"],
        "package": finding["package"],
        "severity": finding["severity"],
    }
    if details:
        value.update(
            {
                "targets": sorted(finding["targets"]),
                "installed_versions": sorted(finding["installed_versions"]),
                "fixed_versions": sorted(finding["fixed_versions"]),
            }
        )
    return value


def _baseline_findings(
    baseline: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    if baseline.get("schema_version") != 1:
        raise InputError("baseline schema_version must be 1")
    if baseline.get("policy") != POLICY:
        raise InputError(f"baseline policy must be {POLICY!r}")
    if baseline.get("accepted_stage") != "A":
        raise InputError("baseline accepted_stage must be 'A'")
    if baseline.get("blocking_severities") != sorted(BLOCKING_SEVERITIES):
        raise InputError("baseline blocking_severities must be CRITICAL and HIGH")
    key_fields = baseline.get("key_fields")
    if key_fields != ["VulnerabilityID", "PkgName"]:
        raise InputError("baseline key_fields must be ['VulnerabilityID', 'PkgName']")
    values = baseline.get("findings")
    if not isinstance(values, list):
        raise InputError("baseline findings must be a list")
    findings: dict[tuple[str, str], dict[str, Any]] = {}
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            raise InputError(f"baseline findings[{index}] must be an object")
        vulnerability_id = _required_text(
            value.get("vulnerability_id"),
            f"baseline findings[{index}].vulnerability_id",
        )
        package = _required_text(
            value.get("package"), f"baseline findings[{index}].package"
        )
        severity = _required_text(
            value.get("severity"), f"baseline findings[{index}].severity"
        ).upper()
        if severity not in BLOCKING_SEVERITIES:
            raise InputError(
                f"baseline findings[{index}] has non-blocking severity {severity}"
            )
        key = (vulnerability_id, package)
        if key in findings:
            raise InputError(
                f"baseline repeats finding key {vulnerability_id}/{package}"
            )
        findings[key] = {
            "vulnerability_id": vulnerability_id,
            "package": package,
            "severity": severity,
        }
    if baseline.get("finding_count") != len(findings):
        raise InputError("baseline finding_count does not match findings")
    return findings


def _image_source(report_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    metadata = report.get("Metadata") or {}
    image_config = metadata.get("ImageConfig") or {}
    config = image_config.get("config") or {}
    labels = config.get("Labels") or {}
    return {
        "artifact_name": str(report.get("ArtifactName") or "unknown"),
        "image_id": str(
            metadata.get("ImageID") or report.get("ArtifactID") or "unknown"
        ),
        "source_ref": str(labels.get("org.opencontainers.image.revision") or "unknown"),
        "pytorch_flavor": str(labels.get("org.towerscout.pytorch.flavor") or "unknown"),
        "report_created_at": str(report.get("CreatedAt") or "unknown"),
        "raw_report_sha256": _sha256(report_path),
    }


def create_baseline(args: argparse.Namespace) -> int:
    reports = [(path, _load_json(path, "Trivy scan")) for path in args.scan]
    extracted = [
        _extract_findings(report, f"Trivy scan {path}") for path, report in reports
    ]
    first_keys = set(extracted[0])
    for (path, _report), findings in zip(reports[1:], extracted[1:]):
        if set(findings) != first_keys:
            added = sorted(set(findings) - first_keys)
            removed = sorted(first_keys - set(findings))
            raise InputError(
                f"baseline scans do not have identical finding keys ({path}: +{len(added)} -{len(removed)})"
            )
    merged = extracted[0]
    for findings in extracted[1:]:
        for key, finding in findings.items():
            if (
                SEVERITY_ORDER[finding["severity"]]
                > SEVERITY_ORDER[merged[key]["severity"]]
            ):
                merged[key]["severity"] = finding["severity"]
    baseline = {
        "schema_version": 1,
        "policy": POLICY,
        "accepted_stage": "A",
        "description": "Accepted pre-TASK-103 HIGH/CRITICAL Trivy finding keys; publishing blocks only additions.",
        "created_utc": args.created_utc,
        "scanner": {
            "name": "Trivy",
            "version": _required_text(
                reports[0][1].get("Trivy", {}).get("Version"), "Trivy.Version"
            ),
            "database_updated_at": args.database_updated_at,
        },
        "blocking_severities": sorted(BLOCKING_SEVERITIES),
        "key_fields": ["VulnerabilityID", "PkgName"],
        "applicable_publish_flavors": ["cpu", "cuda128"],
        "sources": [_image_source(path, report) for path, report in reports],
        "finding_count": len(merged),
        "findings": [
            _serializable_finding(merged[key], details=False) for key in sorted(merged)
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _write_text(args.out, json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out} with {len(merged)} accepted HIGH/CRITICAL keys")
    return 0


def _markdown_table(findings: Iterable[dict[str, Any]], disposition: str) -> list[str]:
    lines = [
        "| Finding | Package | Severity | Installed | Fixed | Disposition |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    values = list(findings)
    if not values:
        lines.append("| none | - | - | - | - | PASS |")
        return lines
    for finding in values:
        installed = ", ".join(finding.get("installed_versions") or []) or "not listed"
        fixed = ", ".join(finding.get("fixed_versions") or []) or "not listed"
        lines.append(
            f"| {finding['vulnerability_id']} | {finding['package']} | {finding['severity']} | "
            f"{installed} | {fixed} | {disposition} |"
        )
    return lines


def compare(args: argparse.Namespace) -> int:
    baseline_doc = _load_json(args.baseline, "baseline")
    baseline = _baseline_findings(baseline_doc)
    flavors = baseline_doc.get("applicable_publish_flavors")
    if not isinstance(flavors, list) or args.flavor not in flavors:
        raise InputError(f"baseline is not declared for publish flavor {args.flavor}")
    report = _load_json(args.candidate, "candidate Trivy scan")
    baseline_scanner = baseline_doc.get("scanner") or {}
    candidate_scanner = report.get("Trivy") or {}
    baseline_version = _required_text(
        baseline_scanner.get("version"), "baseline scanner.version"
    )
    candidate_version = _required_text(
        candidate_scanner.get("Version"), "candidate Trivy.Version"
    )
    if candidate_version != baseline_version:
        raise InputError(
            f"candidate Trivy version {candidate_version!r} does not match "
            f"baseline {baseline_version!r}"
        )
    candidate = _extract_findings(report, "candidate Trivy scan")
    baseline_keys = set(baseline)
    candidate_keys = set(candidate)
    new_keys = sorted(candidate_keys - baseline_keys)
    resolved_keys = sorted(baseline_keys - candidate_keys)
    new_findings = [
        _serializable_finding(candidate[key], details=True) for key in new_keys
    ]
    resolved_findings = [baseline[key] for key in resolved_keys]
    passed = not new_findings
    delta = {
        "schema_version": 1,
        "policy": POLICY,
        "generated_utc": _utc_now(),
        "source_ref": args.source_ref,
        "pytorch_flavor": args.flavor,
        "image": args.image,
        "candidate_artifact": report.get("ArtifactName"),
        "candidate_report_sha256": _sha256(args.candidate),
        "baseline_path": args.baseline.as_posix(),
        "baseline_sha256": _sha256(args.baseline),
        "baseline_count": len(baseline),
        "candidate_count": len(candidate),
        "retained_count": len(baseline_keys & candidate_keys),
        "new_count": len(new_findings),
        "resolved_count": len(resolved_findings),
        "new_findings": new_findings,
        "resolved_findings": resolved_findings,
        "passed": passed,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    _write_text(args.json_out, json.dumps(delta, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Exact-digest image scan delta disposition",
        "",
        f"- Image: `{args.image}`",
        f"- Source ref: `{args.source_ref}`",
        f"- PyTorch flavor: `{args.flavor}`",
        f"- Baseline: `{args.baseline.as_posix()}`",
        f"- Baseline SHA-256: `{delta['baseline_sha256']}`",
        f"- Policy: block every new CRITICAL/HIGH `(VulnerabilityID, PkgName)` key.",
        f"- Counts: baseline {len(baseline)}; candidate {len(candidate)}; "
        f"new {len(new_findings)}; resolved {len(resolved_findings)}.",
        f"- Outcome: **{'PASS' if passed else 'BLOCK'}**",
        "",
        "## New HIGH/CRITICAL findings",
        "",
        *_markdown_table(new_findings, "BLOCK - new versus committed baseline"),
        "",
        "## Resolved HIGH/CRITICAL findings",
        "",
        *_markdown_table(resolved_findings, "RESOLVED in candidate"),
        "",
        "Unchanged accepted-baseline findings are counted above and remain individually auditable in the committed baseline.",
    ]
    _write_text(args.markdown_out, "\n".join(lines) + "\n")
    print(
        f"TASK-103 Trivy delta {'PASS' if passed else 'BLOCK'}: "
        f"baseline={len(baseline)} candidate={len(candidate)} new={len(new_findings)} resolved={len(resolved_findings)}"
    )
    return 0 if passed else 1


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser(
        "create-baseline", help="normalize matching accepted scans"
    )
    create.add_argument("--scan", action="append", required=True, type=Path)
    create.add_argument("--database-updated-at", required=True)
    create.add_argument("--created-utc", required=True)
    create.add_argument("--out", required=True, type=Path)
    create.set_defaults(handler=create_baseline)

    check = subparsers.add_parser(
        "compare", help="compare a candidate scan with the baseline"
    )
    check.add_argument("--baseline", required=True, type=Path)
    check.add_argument("--candidate", required=True, type=Path)
    check.add_argument("--flavor", required=True, choices=("cpu", "cuda128"))
    check.add_argument("--image", required=True)
    check.add_argument("--source-ref", required=True)
    check.add_argument("--markdown-out", required=True, type=Path)
    check.add_argument("--json-out", required=True, type=Path)
    check.set_defaults(handler=compare)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        return args.handler(args)
    except InputError as exc:
        print(f"task103_trivy_delta: error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"task103_trivy_delta: IO error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
