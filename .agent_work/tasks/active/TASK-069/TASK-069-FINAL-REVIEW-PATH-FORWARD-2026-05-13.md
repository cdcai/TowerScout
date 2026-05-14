# TASK-069 Final Roadmap Review - Path Forward

> 2026-05-13 update: This path-forward review is superseded for Sprint 06 by
> `TASK-069-AGPL-YOLO-RELEASE-IMPLEMENTATION-2026-05-13.md` where the team
> chose to seek feedback on a YOLO-enabled `agpl-yolo` RC/pilot path. The ONNX
> runtime migration moves to a later permissive Apache-only release track unless
> reviewers reject AGPL as the release posture.

Date: 2026-05-13
Reviewed source: `TowerScout Final Strategy Roadmap Review_2026.05.13.docx`
Related roadmap: `.agent_work/tasks/active/TASK-069/TASK-069-FINAL-STRATEGY-ROADMAP-2026-05-12.md`

## Executive Conclusion

The reviewer supports the roadmap as final in substance and does not recommend another strategy redesign. I agree with that assessment.

The remaining work is an execution and precision pass, not a strategy reset. The correct path forward is:

1. Continue the restricted pilot / V1 RC1 path.
2. Keep the public compliant release blocked until the named public-release gates are closed.
3. Perform one short precision pass to turn the remaining caveats into concrete implementation tasks, signoffs, and release blockers.
4. Then execute the roadmap through the existing Sprint 06 and backlog structure.

The restricted pilot and public release must remain separate in language, packaging, and approval criteria.

## Reviewer Feedback Summary

The reviewer agreed with the main roadmap decisions:

- The two-track model is correct: restricted pilot now, public compliant release later.
- TowerScout should be framed as an OCI-containerized local application.
- Podman should be preferred for end-user/release use.
- Docker Desktop should remain only an approved fallback.
- GitHub Releases should remain the user-facing delivery channel.
- Model and data assets should remain separate from the Apache-licensed source.
- Manual/local model import is the right default until redistribution authority is documented.
- Ultralytics/YOLO remains a hard public-release blocker.
- ONNX Runtime is the right preferred evaluation target, but not yet a guaranteed final answer.
- Public model/data import should be allowlist-only.
- Provider/API terms need their own packaged artifact.
- Revocation needs a real runbook.
- The public repo should be a clean curated release line.

The reviewer also confirmed the open questions:

| Question | Reviewer answer | Path-forward interpretation |
| --- | --- | --- |
| Clean public release line vs legacy history | Prefer clean public release line | Plan for curated public branch/repo, not publishing legacy history as-is |
| Manual model import until permission | Yes | Keep manual/local import as the default until written redistribution authority exists |
| ONNX Runtime | Preferred evaluation target, not final until PoC | Start with ONNX PoC, but keep one alternate runtime option available if ONNX fails |
| Podman-first scope | Enforce immediately for release/end-user launch paths; review developer workflow separately | Change release launcher behavior first; avoid breaking developer workflows without review |
| GPU support | Optional validated image/profile or explicitly out of supported baseline | Prioritize decision/design now; do not make unsupported GPU claims |
| Public repo exclusions | Needs explicit inclusion/exclusion list | Create clean-line inventory before public release |
| Provider terms | Framework is right if specific enough | Add `PROVIDER_TERMS.md` and Setup Wizard/docs references |
| Revocation mechanics | Strategically right, operationally incomplete | Add concrete runbook before final release governance is complete |

## Path Forward By Track

### Track 1: Restricted Pilot / V1 RC1

Goal: let non-technical pilot users deploy TowerScout locally from GitHub Release assets without claiming public Apache/open-source compliance yet.

Continue the current Sprint 06 lane:

1. `TASK-071` - End-user release package documentation.
2. `TASK-066` - Release candidate validation gate.
3. `TASK-073` - Clean-machine pilot / UAT execution plan.

Bring forward if needed, and likely soon:

4. `TASK-074` - Runtime prerequisite preflight.

Pilot release posture:

- Use GitHub Release control ZIP.
- Use pinned GHCR image digest.
- Use manifest-backed local asset import.
- Use support-managed image preload for restricted networks.
- Do not promise release-provided OCI archive packaging yet.
- Do not label the pilot as the public compliant Apache-2.0 release.

Pilot exit criteria:

- A clean Windows 11 AMD64 user path works.
- Podman path is clear and validated.
- Docker fallback is documented only as optional/site-approved.
- Asset placement/import is understandable.
- Setup Wizard config persists.
- One bounded detection smoke works.
- Support/diagnostic collection does not leak secrets or sensitive user data.

### Track 2: Precision Pass Before Broad Circulation

Goal: make the roadmap final in form, not just strategy.

Required precision-pass items:

1. Remove drafting artifacts from the reviewer-facing strategy document.
2. Convert internal citation markers to normal footnotes/links.
3. Add the exact public-release blocker table.
4. Add explicit "supported now" vs "future productized" restricted-network language.
5. Add provider/API terms packaging requirements.
6. Add GitHub-native vs fallback control language.
7. Add allowlist-only model/data import language.
8. Add the revocation runbook.
9. Add signoff owners for rights, model redistribution, provider terms, history, and compliance payload.

This should be a short document-editing and task-definition pass, not another planning cycle.

### Track 3: Policy And Compliance Governance

Goal: resolve whether and how a public Apache-2.0 release can happen.

Pull `TASK-069` into active work.

Required outputs:

- Rights evidence pack.
- File-level ownership/provenance inventory.
- Contributor authority record.
- Third-party provenance log.
- Model-rights packet.
- Data-terms packet.
- Provider-terms packet.
- Public-history decision memo.
- Clean public line inclusion/exclusion inventory.
- Public-release approval memo.

Default decisions unless changed by owner/legal review:

- Apache-2.0 applies only to provably TowerScout-authored code.
- Public release uses a clean curated line.
- Model weights are separate from source code.
- Manual model import remains default until written redistribution authority exists.
- Public release excludes internal planning artifacts, vendored YOLO/Ultralytics, model weights, raw data assets, and unsupported provider drift.

Required signoffs:

- J-Schulein plus legal/rights reviewer for rights evidence and history.
- Model owner/licensor plus legal for model redistribution.
- Product owner plus legal for provider terms.
- Release owner plus legal/compliance reviewer for final ZIP/image compliance payload.

### Track 4: Runtime And Packaging Corrections

Goal: make the implementation match the strategy.

Priority implementation tasks:

1. Podman-first release launcher behavior.
   - Change release/end-user auto-detection to prefer Podman.
   - Keep Docker as explicit fallback.
   - Detect/log Compose provider.
   - Preserve developer workflow until reviewed.

2. Runtime preflight.
   - Check Podman install, Podman machine, Compose provider, ports, image availability, assets, disk, TLS bundle, provider config, and platform prerequisites.

3. Compliance payload in release package and image.
   - Add `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, release manifest, checksums, and SBOM references.

4. Release manifest and integrity.
   - Tie together app version, ZIP hash, image digest, asset manifest, asset hashes, model/data versions, model terms version, SBOM, and track type.

5. Staged allowlist-only asset import.
   - Stage first.
   - Verify manifest/hash/size.
   - Activate only after validation.
   - Preserve previous active asset set on failure.

6. Revocation runbook.
   - Define bad ZIP, bad image digest, bad model/data asset, and license-defective release workflows.
   - Include user notification, rollback target, manifest update, and asset retirement.

### Track 5: Provider/API Terms And Key Policy

Goal: make provider obligations explicit and align setup/docs with reality.

Pull `TASK-076` into active or near-active work.

Required outputs:

- `PROVIDER_TERMS.md`.
- Setup Wizard/user-doc references.
- Provider key restriction guidance.
- Google/Azure-specific notes on attribution, caching, map/tile use, geocoding/result handling, use with third-party maps, and provider-side account obligations.
- Decision on Bing drift: remove from public line or document as unsupported legacy compatibility.

Important position:

Open-sourcing TowerScout code does not grant rights to Google Maps Platform, Azure Maps, imagery, tiles, geocoding output, provider caching, or redistribution.

### Track 6: Public ML Runtime Migration

Goal: remove the current AGPL/Ultralytics blocker from the public default runtime while preserving TowerScout's detection workflow.

Current hard blockers:

- `webapp/requirements.txt` pins `ultralytics==8.3.249`.
- `webapp/vendor/yolov5_local/` contains AGPL YOLO code.
- `webapp/ts_yolov5.py` imports the local YOLO loader.
- `webapp/ts_en.py` uses `EfficientNet.from_pretrained()` and `torch.load()`.

Path:

1. Define detector/classifier interfaces.
2. Run ONNX Runtime PoC for detector and classifier together.
3. Verify preprocessing, postprocessing, confidence handling, NMS, output schema, accuracy, CPU performance, and GPU provider behavior.
4. Evaluate one alternate non-Ultralytics runtime only if ONNX fails or creates unacceptable tradeoffs.
5. Remove Ultralytics and vendored YOLO from the public default release path.
6. Replace unsafe/untrusted `.pt` loading in public builds.

Exit criteria:

- Public default runtime has no Ultralytics/YOLO AGPL dependency.
- Public runtime does not load untrusted pickle-backed model files.
- Detection/review/export behavior remains compatible.
- Accuracy/performance changes are documented and accepted.

### Track 7: GPU Capability With CPU Fallback

Goal: prioritize GPU capability without undermining the stable CPU baseline.

Pull `TASK-075` forward as an early decision/design task.

Recommended policy:

- CPU remains the guaranteed supported baseline.
- GPU is optional acceleration.
- Public GPU support must be validated, not merely claimed.
- GPU should either ship as a separate optional image/profile or stay out of scope until validated.

Implementation direction:

- Add `TOWERSCOUT_DEVICE=auto|cpu|cuda`.
- Add `TOWERSCOUT_REQUIRE_GPU=0|1`.
- Report GPU availability and selected runtime in readiness/status.
- For PyTorch-restricted pilot, use `torch.cuda.is_available()` and CPU fallback.
- For ONNX public runtime, evaluate `CUDAExecutionProvider` with `CPUExecutionProvider` fallback.
- Avoid bloating the default public image with GPU dependencies unless validated and accepted.

Exit criteria:

- CPU-only systems work.
- GPU-capable systems can use GPU when configured/available.
- Failed GPU initialization falls back to CPU unless GPU is explicitly required.
- Docs distinguish validated GPU support from future/best-effort work.

### Track 8: Public Codebase Cleanup And Refactor

Goal: make the public work product clean, maintainable, and appropriate to publish.

This should happen after the restricted pilot baseline is stable enough to regression-test, but before public release.

Backend cleanup:

- Split `webapp/towerscout.py` into clearer route/service boundaries.
- Move detection orchestration behind explicit service interfaces.
- Isolate detector/classifier runtime.
- Consolidate provider availability/config logic.
- Remove or quarantine Bing drift.
- Standardize structured errors and logging.
- Implement safe support-bundle allowlist.

Frontend cleanup:

- Preserve existing modular `webapp/js/src/` layout.
- Treat generated `webapp/js/towerscout.js` as build output.
- Consider `TASK-060` frontend build modernization after release path stabilizes.
- Preserve Google/Azure provider switching, review, manual tower, and export behavior.

Repo hygiene:

- Exclude `.agent_work` from clean public line unless intentionally curated.
- Exclude model weights and raw data assets.
- Exclude training notebooks/scratch artifacts unless intentionally public.
- Remove unsupported provider drift from public docs/config.
- Normalize license headers after Apache-2.0 authority is established.
- Run secret, large-file, license, and internal-reference scans.

### Track 9: CI And Release Gates

Goal: automate the gates that should not depend on memory or manual review.

Pull `TASK-067` and `TASK-068` after the RC checklist is stable, or earlier if validation is fragile.

Required gates:

- Package assembly test.
- Compliance file presence test.
- Release manifest schema test.
- Image digest/pinning test.
- Asset manifest/hash consistency test.
- Prohibited dependency/path scan.
- License scan.
- Secret scan.
- Large-file/model-data tracking scan.
- SBOM generation.
- Windows/PowerShell script validation.
- Node LTS migration plan.

Strategy:

- Use GitHub-native features where available.
- Use equivalent CI/local tools where GitHub plan/repo visibility limits a feature.

## Recommended Execution Order

### Immediate

1. Treat reviewer report as confirming the strategy.
2. Do the short precision pass on the roadmap document.
3. Pull `TASK-069`, `TASK-076`, and `TASK-075` into the active planning lane or assign owners.
4. Continue `TASK-071` with the updated strategy assumptions.

### Before Restricted Pilot

5. Validate end-user docs and package path.
6. Fix or document Podman-first release behavior.
7. Run `TASK-066`.
8. Pull `TASK-074` if preflight friction appears, or proactively if capacity allows.
9. Complete `TASK-073`.

### Before Public Compliant Release

10. Finish rights evidence and public-history decision.
11. Add compliance/provider/model/data notices to ZIP and image.
12. Implement staged allowlist-only asset import.
13. Add release manifest, SBOM, checksums, and revocation runbook.
14. Replace public default Ultralytics/YOLO runtime path.
15. Resolve EfficientNet/`torch.load()` public runtime risk.
16. Decide and validate GPU support model.
17. Complete cleanup/refactor tranche.
18. Create clean public release line.
19. Run clean-laptop public release acceptance test.
20. Obtain final owner/legal/reviewer signoff.

## Current Position

The path forward is now clear:

- No more strategy redesign is needed.
- One precision pass is still needed before broad circulation.
- Restricted pilot work can continue.
- Public compliant release remains blocked by known, named gates.
- The most urgent engineering alignment items are Podman-first release behavior, provider terms, compliance payload packaging, staged asset import, and release manifest/revocation mechanics.
- The largest public-release engineering item remains the ML runtime migration away from the current Ultralytics/YOLO path.

## Sources Checked

- Apache license application guidance: https://www.apache.org/legal/apply-license
- Apache LICENSE/NOTICE distribution guidance: https://infra.apache.org/licensing-howto.html
- Podman Compose documentation: https://docs.podman.io/en/v5.6.2/markdown/podman-compose.1.html
- GitHub artifact attestations: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- GitHub Releases: https://docs.github.com/repositories/releasing-projects-on-github/about-releases
- Docker SBOM attestations: https://docs.docker.com/build/metadata/attestations/sbom/
- PyTorch `torch.load`: https://docs.pytorch.org/docs/2.9/generated/torch.load.html
- Google Maps Platform Service Specific Terms: https://cloud.google.com/maps-platform/terms/maps-service-terms?hl=en_US
- Microsoft Azure Maps Product Terms: https://www.microsoft.com/licensing/terms/en-US/productoffering/MicrosoftAzureServices/MCA/
