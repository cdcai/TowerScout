---
name: towerscout-release-compliance-review
description: Primary skill only when TowerScout license, notice, AGPL/YOLO, model/data/provider
  terms, source/SBOM, /license, or public release wording changes. For broader RC
  validation, use towerscout-release-candidate-gate first and this as a secondary
  check.
---

# TowerScout Release Compliance Review

Use this skill when a task touches licenses, notices, model/data/provider terms, AGPL/YOLO posture, release manifests, source notices, SBOM references, README license claims, package metadata, or public release wording.

## Goal

Identify release-policy inconsistencies and missing artifacts; do not provide legal approval.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Boundary

This skill helps identify inconsistencies and missing artifacts. It does not provide legal approval. For legal or release policy decisions, summarize findings and defer to the project owner/legal reviewer.

## Primary versus secondary

Use this as the primary skill only when compliance, license, notice, model/data/provider terms, source/SBOM, or public release wording changed. For full RC validation, use `towerscout-release-candidate-gate` first and this only as a focused secondary check.

## First read

Read files that exist among:

- `.agent_work/current-tasks.md`
- `README.md`
- `package.json`
- `LICENSE`, `LICENSE.TXT`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md`
- `PROVIDER_TERMS.md`
- `SOURCE.txt`
- `SBOM.txt`
- `release-manifest.v1.json`
- `docs/release-asset-bundle-contract.md`
- `.github/workflows/container-publish.yml`

## Review checklist

1. Flag conflicting claims such as MIT, Apache-only, CC-BY-NC-SA, AGPL-governed package, or public release wording that are not clearly scoped.
2. Distinguish TowerScout-authored code license from the full YOLO-enabled package/image posture.
3. Confirm YOLO/Ultralytics notices and model-weight labels match accepted release posture.
4. Confirm source notice/ref, SBOM reference, release manifest, checksums, image digest, and revocation/support notes are included when required.
5. Confirm Google/Azure/provider API key and imagery terms are not overridden or misrepresented.
6. Confirm end-user docs tell users where to find source/license/provider/model/data notices.

## Inspect commands (read-only)

```bash
python .agents/skills/towerscout-release-compliance-review/scripts/scan_license_claims.py
git diff -- README.md package.json LICENSE* NOTICE* THIRD_PARTY_NOTICES.md MODEL_LICENSES.md DATA_LICENSES.md PROVIDER_TERMS.md SOURCE.txt SBOM.txt release-manifest.v1.json docs .github/workflows/container-publish.yml
```

## Build/update generated files (mutating)

No standard mutating command. Do not rewrite legal/compliance files automatically beyond the requested edits; surface owner/legal questions explicitly.

## Validation commands

```bash
python -m pytest tests/unit/test_license_notices.py tests/unit/test_release_manifest_schema.py tests/unit/test_container_publish_workflow.py -q -p no:cacheprovider
python .agent_work/scripts/validate_agent_work.py
git diff --check
```

## Output format

Return blocking inconsistencies, non-blocking wording or artifact follow-ups, files inspected, tests run, and questions requiring owner/legal/reviewer decision.
