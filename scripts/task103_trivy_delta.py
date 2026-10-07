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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

BLOCKING_SEVERITIES = frozenset({"HIGH", "CRITICAL"})
SEVERITY_ORDER = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
POLICY = "task103-g10-no-new-high-critical"
RESIDUAL_POLICY = "task103-g10-time-bounded-residuals"
SUPPORTED_FLAVORS = frozenset({"cpu", "cuda128"})
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

BASELINE_FIELDS = frozenset(
    {
        "schema_version",
        "policy",
        "accepted_stage",
        "description",
        "created_utc",
        "scanner",
        "blocking_severities",
        "key_fields",
        "applicable_publish_flavors",
        "sources",
        "finding_count",
        "findings",
    }
)
BASELINE_SCANNER_FIELDS = frozenset({"name", "version", "database_updated_at"})
BASELINE_SOURCE_FIELDS = frozenset(
    {
        "artifact_name",
        "image_id",
        "source_ref",
        "pytorch_flavor",
        "report_created_at",
        "raw_report_sha256",
    }
)
BASELINE_FINDING_FIELDS = frozenset(
    {"vulnerability_id", "package", "severity"}
)
RESIDUAL_FIELDS = frozenset(
    {"schema_version", "policy", "description", "findings"}
)
RESIDUAL_FINDING_FIELDS = frozenset(
    {
        "vulnerability_id",
        "package",
        "severity",
        "installed_version",
        "package_id",
        "package_class",
        "package_type",
        "applicable_publish_flavors",
        "expires_utc",
        "reason",
        "compensating_controls",
        "approved_by",
        "follow_up_task",
    }
)


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


def _reject_unknown_fields(
    value: dict[str, Any], allowed: frozenset[str], label: str
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputError(f"{label} has unknown fields: {', '.join(unknown)}")


def _required_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise InputError(f"{label} must be a non-empty list")
    values = [_required_text(item, f"{label}[]") for item in value]
    if len(values) != len(set(values)):
        raise InputError(f"{label} must not contain duplicates")
    return values


def _parse_utc(value: Any, label: str) -> datetime:
    text = _required_text(value, label)
    if not text.endswith("Z"):
        raise InputError(f"{label} must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise InputError(f"{label} must be a valid UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise InputError(f"{label} must be UTC")
    return parsed


def _string_values(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, str):
        return []
    return [value] if value else []


def _extract_findings(
    report: dict[str, Any], label: str
) -> dict[tuple[str, str], dict[str, Any]]:
    if "Results" not in report:
        raise InputError(f"{label}.Results is required")
    results = report["Results"]
    if not isinstance(results, list) or not results:
        raise InputError(f"{label}.Results must be a non-empty list")
    findings: dict[tuple[str, str], dict[str, Any]] = {}
    result_kinds: set[tuple[str, str]] = set()
    for result_index, result in enumerate(results):
        if not isinstance(result, dict):
            raise InputError(f"{label}.Results[{result_index}] must be an object")
        target = _required_text(
            result.get("Target"), f"{label}.Results[{result_index}].Target"
        )
        package_class = _required_text(
            result.get("Class"), f"{label}.Results[{result_index}].Class"
        )
        package_type = _required_text(
            result.get("Type"), f"{label}.Results[{result_index}].Type"
        )
        result_kinds.add((package_class, package_type))
        if "Vulnerabilities" not in result:
            raise InputError(
                f"{label}.Results[{result_index}].Vulnerabilities is required"
            )
        vulnerabilities = result["Vulnerabilities"]
        if vulnerabilities is None:
            vulnerabilities = []
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
                    "package_ids": set(),
                    "package_classes": set(),
                    "package_types": set(),
                    "installed_versions": set(),
                    "fixed_versions": set(),
                },
            )
            if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(
                entry["severity"], 0
            ):
                entry["severity"] = severity
            entry["targets"].add(target)
            entry["package_ids"].update(_string_values(vulnerability.get("PkgID")))
            entry["package_classes"].add(package_class)
            entry["package_types"].add(package_type)
            entry["installed_versions"].update(
                _string_values(vulnerability.get("InstalledVersion"))
            )
            entry["fixed_versions"].update(
                _string_values(vulnerability.get("FixedVersion"))
            )
    required_kinds = {("os-pkgs", "debian"), ("lang-pkgs", "python-pkg")}
    missing_kinds = sorted(required_kinds - result_kinds)
    if missing_kinds:
        rendered = ", ".join(f"{kind}/{package_type}" for kind, package_type in missing_kinds)
        raise InputError(f"{label}.Results is missing required scan groups: {rendered}")
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
                "package_ids": sorted(finding["package_ids"]),
                "package_classes": sorted(finding["package_classes"]),
                "package_types": sorted(finding["package_types"]),
                "installed_versions": sorted(finding["installed_versions"]),
                "fixed_versions": sorted(finding["fixed_versions"]),
            }
        )
    return value


def _baseline_findings(
    baseline: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    _reject_unknown_fields(baseline, BASELINE_FIELDS, "baseline")
    if baseline.get("schema_version") != 1:
        raise InputError("baseline schema_version must be 1")
    if baseline.get("policy") != POLICY:
        raise InputError(f"baseline policy must be {POLICY!r}")
    if baseline.get("accepted_stage") != "A":
        raise InputError("baseline accepted_stage must be 'A'")
    if baseline.get("blocking_severities") != sorted(BLOCKING_SEVERITIES):
        raise InputError("baseline blocking_severities must be CRITICAL and HIGH")
    scanner = baseline.get("scanner")
    if not isinstance(scanner, dict):
        raise InputError("baseline scanner must be an object")
    _reject_unknown_fields(scanner, BASELINE_SCANNER_FIELDS, "baseline scanner")
    if scanner.get("name") != "Trivy":
        raise InputError("baseline scanner.name must be 'Trivy'")
    _required_text(scanner.get("version"), "baseline scanner.version")
    _required_text(
        scanner.get("database_updated_at"), "baseline scanner.database_updated_at"
    )
    key_fields = baseline.get("key_fields")
    if key_fields != ["VulnerabilityID", "PkgName"]:
        raise InputError("baseline key_fields must be ['VulnerabilityID', 'PkgName']")
    values = baseline.get("findings")
    if not isinstance(values, list):
        raise InputError("baseline findings must be a list")
    sources = baseline.get("sources")
    if not isinstance(sources, list) or not sources:
        raise InputError("baseline sources must be a non-empty list")
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise InputError(f"baseline sources[{index}] must be an object")
        _reject_unknown_fields(
            source, BASELINE_SOURCE_FIELDS, f"baseline sources[{index}]"
        )
        for field in BASELINE_SOURCE_FIELDS:
            _required_text(source.get(field), f"baseline sources[{index}].{field}")
    findings: dict[tuple[str, str], dict[str, Any]] = {}
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            raise InputError(f"baseline findings[{index}] must be an object")
        _reject_unknown_fields(
            value, BASELINE_FINDING_FIELDS, f"baseline findings[{index}]"
        )
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


def _accepted_residuals(
    residuals: dict[str, Any], flavor: str
) -> dict[tuple[str, str], dict[str, Any]]:
    _reject_unknown_fields(residuals, RESIDUAL_FIELDS, "accepted residuals")
    if residuals.get("schema_version") != 1:
        raise InputError("accepted residuals schema_version must be 1")
    if residuals.get("policy") != RESIDUAL_POLICY:
        raise InputError(f"accepted residuals policy must be {RESIDUAL_POLICY!r}")
    _required_text(residuals.get("description"), "accepted residuals description")
    values = residuals.get("findings")
    if not isinstance(values, list):
        raise InputError("accepted residuals findings must be a list")

    now = datetime.now(timezone.utc)
    accepted: dict[tuple[str, str], dict[str, Any]] = {}
    seen_keys: set[tuple[str, str]] = set()
    for index, value in enumerate(values):
        label = f"accepted residuals findings[{index}]"
        if not isinstance(value, dict):
            raise InputError(f"{label} must be an object")
        _reject_unknown_fields(value, RESIDUAL_FINDING_FIELDS, label)
        vulnerability_id = _required_text(
            value.get("vulnerability_id"), f"{label}.vulnerability_id"
        )
        package = _required_text(value.get("package"), f"{label}.package")
        severity = _required_text(value.get("severity"), f"{label}.severity").upper()
        if severity not in BLOCKING_SEVERITIES:
            raise InputError(f"{label}.severity must be HIGH or CRITICAL")
        flavors = _required_string_list(
            value.get("applicable_publish_flavors"),
            f"{label}.applicable_publish_flavors",
        )
        if not set(flavors) <= SUPPORTED_FLAVORS:
            raise InputError(f"{label} names an unsupported publish flavor")
        expires = _parse_utc(value.get("expires_utc"), f"{label}.expires_utc")
        if expires <= now:
            raise InputError(f"{label} expired at {value['expires_utc']}")
        controls = _required_string_list(
            value.get("compensating_controls"), f"{label}.compensating_controls"
        )
        key = (vulnerability_id, package)
        if key in seen_keys:
            raise InputError(
                f"accepted residuals repeats finding key {vulnerability_id}/{package}"
            )
        seen_keys.add(key)
        normalized = {
            "vulnerability_id": vulnerability_id,
            "package": package,
            "severity": severity,
            "installed_version": _required_text(
                value.get("installed_version"), f"{label}.installed_version"
            ),
            "package_id": _required_text(
                value.get("package_id"), f"{label}.package_id"
            ),
            "package_class": _required_text(
                value.get("package_class"), f"{label}.package_class"
            ),
            "package_type": _required_text(
                value.get("package_type"), f"{label}.package_type"
            ),
            "applicable_publish_flavors": flavors,
            "expires_utc": value["expires_utc"],
            "reason": _required_text(value.get("reason"), f"{label}.reason"),
            "compensating_controls": controls,
            "approved_by": _required_text(
                value.get("approved_by"), f"{label}.approved_by"
            ),
            "follow_up_task": _required_text(
                value.get("follow_up_task"), f"{label}.follow_up_task"
            ),
        }
        if flavor in flavors:
            accepted[key] = normalized
    return accepted


def _validate_candidate_identity(
    report: dict[str, Any], args: argparse.Namespace
) -> str:
    if report.get("SchemaVersion") != 2:
        raise InputError("candidate Trivy scan SchemaVersion must be 2")
    artifact_name = _required_text(
        report.get("ArtifactName"), "candidate Trivy scan ArtifactName"
    )
    if artifact_name != args.image:
        raise InputError(
            f"candidate artifact {artifact_name!r} does not match --image {args.image!r}"
        )
    metadata = report.get("Metadata")
    if not isinstance(metadata, dict):
        raise InputError("candidate Trivy scan Metadata must be an object")
    image_id = _required_text(
        metadata.get("ImageID"), "candidate Trivy scan Metadata.ImageID"
    )
    if not SHA256_RE.fullmatch(image_id):
        raise InputError("candidate Trivy scan Metadata.ImageID must be sha256:<64 hex>")
    if image_id != args.expected_image_id:
        raise InputError(
            f"candidate image ID {image_id!r} does not match --expected-image-id {args.expected_image_id!r}"
        )
    image_config = metadata.get("ImageConfig")
    if not isinstance(image_config, dict):
        raise InputError("candidate Trivy scan Metadata.ImageConfig must be an object")
    config = image_config.get("config")
    if not isinstance(config, dict):
        raise InputError("candidate Trivy scan Metadata.ImageConfig.config must be an object")
    labels = config.get("Labels")
    if not isinstance(labels, dict):
        raise InputError("candidate Trivy scan image labels must be an object")
    source_ref = _required_text(
        labels.get("org.opencontainers.image.revision"),
        "candidate source revision label",
    )
    if source_ref != args.source_ref:
        raise InputError(
            f"candidate source label {source_ref!r} does not match --source-ref {args.source_ref!r}"
        )
    flavor = _required_text(
        labels.get("org.towerscout.pytorch.flavor"), "candidate flavor label"
    )
    if flavor != args.flavor:
        raise InputError(
            f"candidate flavor label {flavor!r} does not match --flavor {args.flavor!r}"
        )
    return image_id


def _residual_matches(
    candidate: dict[str, Any], residual: dict[str, Any]
) -> bool:
    return (
        candidate["severity"] == residual["severity"]
        and candidate["installed_versions"] == {residual["installed_version"]}
        and candidate["package_ids"] == {residual["package_id"]}
        and candidate["package_classes"] == {residual["package_class"]}
        and candidate["package_types"] == {residual["package_type"]}
    )


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
    candidate_image_id = _validate_candidate_identity(report, args)
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
    residual_doc = _load_json(args.accepted_residuals, "accepted residuals")
    residuals = _accepted_residuals(residual_doc, args.flavor)
    baseline_keys = set(baseline)
    candidate_keys = set(candidate)
    new_keys = sorted(candidate_keys - baseline_keys)
    resolved_keys = sorted(baseline_keys - candidate_keys)
    severity_escalation_keys = sorted(
        key
        for key in baseline_keys & candidate_keys
        if SEVERITY_ORDER[candidate[key]["severity"]]
        > SEVERITY_ORDER[baseline[key]["severity"]]
    )
    accepted_residual_keys = sorted(
        key
        for key in new_keys
        if key in residuals and _residual_matches(candidate[key], residuals[key])
    )
    unused_residual_keys = sorted(set(residuals) - set(accepted_residual_keys))
    if unused_residual_keys:
        rendered = ", ".join(f"{key[0]}/{key[1]}" for key in unused_residual_keys)
        raise InputError(
            "accepted residual entries did not match the candidate exactly: " + rendered
        )
    blocking_keys = sorted(set(new_keys) - set(accepted_residual_keys))
    blocking_findings = [
        _serializable_finding(candidate[key], details=True) for key in blocking_keys
    ]
    accepted_baseline_count = len(baseline_keys & candidate_keys) - len(
        severity_escalation_keys
    )
    accepted_residual_findings = [
        {
            **_serializable_finding(candidate[key], details=True),
            "expires_utc": residuals[key]["expires_utc"],
            "approved_by": residuals[key]["approved_by"],
            "follow_up_task": residuals[key]["follow_up_task"],
        }
        for key in accepted_residual_keys
    ]
    severity_escalations = [
        {
            **_serializable_finding(candidate[key], details=True),
            "baseline_severity": baseline[key]["severity"],
        }
        for key in severity_escalation_keys
    ]
    resolved_findings = [baseline[key] for key in resolved_keys]
    passed = not blocking_findings and not severity_escalations
    delta = {
        "schema_version": 1,
        "policy": POLICY,
        "generated_utc": _utc_now(),
        "source_ref": args.source_ref,
        "pytorch_flavor": args.flavor,
        "image": args.image,
        "candidate_artifact": report.get("ArtifactName"),
        "candidate_image_id": candidate_image_id,
        "candidate_report_sha256": _sha256(args.candidate),
        "baseline_path": args.baseline.as_posix(),
        "baseline_sha256": _sha256(args.baseline),
        "accepted_residuals_path": args.accepted_residuals.as_posix(),
        "accepted_residuals_sha256": _sha256(args.accepted_residuals),
        "baseline_count": len(baseline),
        "candidate_count": len(candidate),
        "retained_count": len(baseline_keys & candidate_keys),
        "accepted_baseline_count": accepted_baseline_count,
        "new_count": len(new_keys),
        "accepted_residual_count": len(accepted_residual_findings),
        "blocking_count": len(blocking_findings),
        "severity_escalation_count": len(severity_escalations),
        "resolved_count": len(resolved_findings),
        "accepted_residual_findings": accepted_residual_findings,
        "blocking_findings": blocking_findings,
        "severity_escalations": severity_escalations,
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
        f"- Accepted residuals: `{args.accepted_residuals.as_posix()}`",
        f"- Accepted residuals SHA-256: `{delta['accepted_residuals_sha256']}`",
        f"- Policy: block every unaccepted new CRITICAL/HIGH key and every severity escalation.",
        f"- Counts: baseline {len(baseline)}; candidate {len(candidate)}; "
        f"accepted baseline {accepted_baseline_count}; "
        f"new {len(new_keys)}; accepted residual {len(accepted_residual_findings)}; "
        f"blocking {len(blocking_findings)}; severity escalations {len(severity_escalations)}; "
        f"resolved {len(resolved_findings)}.",
        f"- Outcome: **{'PASS' if passed else 'BLOCK'}**",
        "",
        "## Blocking new HIGH/CRITICAL findings",
        "",
        *_markdown_table(blocking_findings, "BLOCK - not accepted"),
        "",
        "## Accepted time-bounded residual findings",
        "",
        *_markdown_table(accepted_residual_findings, "ACCEPTED - time bounded"),
        "",
        "## Severity escalations",
        "",
        *_markdown_table(severity_escalations, "BLOCK - severity escalation"),
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
        f"baseline={len(baseline)} candidate={len(candidate)} "
        f"accepted_baseline={accepted_baseline_count} new={len(new_keys)} "
        f"accepted_residual={len(accepted_residual_findings)} blocking={len(blocking_findings)} "
        f"severity_escalations={len(severity_escalations)} resolved={len(resolved_findings)}"
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
    check.add_argument("--accepted-residuals", required=True, type=Path)
    check.add_argument("--flavor", required=True, choices=sorted(SUPPORTED_FLAVORS))
    check.add_argument("--image", required=True)
    check.add_argument("--expected-image-id", required=True)
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
