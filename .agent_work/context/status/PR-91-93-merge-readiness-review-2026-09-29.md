# TowerScout Open PR Merge-Readiness Review

**Date:** 2026-09-29
**Scope:** The three open pull requests against `main` — PR #91 (docs: record Task-103 rc3 qualification), PR #92 (fix Podman TLS repair lifecycle), PR #93 (fix cancellation retry readiness race).
**Heads reviewed:** #91 `f70d5ac` · #92 `d6c4333` · #93 `336be9c` · base `main` at `7a5eedd` (the PR #90 merge).
**Method:** Static review of each PR's diff at its current head, CI check-run results, and review-thread history, with targeted verification of the referenced helpers and API contracts in each PR's tree and on `main`. No code was executed as part of this review.

## Verdicts at a glance

| PR | Title | Verdict |
| --- | --- | --- |
| #92 | Fix Podman TLS repair lifecycle | **Ready to merge** |
| #93 | Fix cancellation retry readiness race | **Ready to merge** |
| #91 | docs: record Task-103 rc3 qualification | **Hold — two documentation reconciliations, then merge last** |

All three PRs report a clean mergeable state against current `main` and pass the full 10-check CI matrix (the `build` check is skipped by design for non-publishing changes). The three PRs touch disjoint file sets, so no merge order can produce git conflicts; the sequencing recommendation at the end is about content dependencies, not mechanics.

## PR #92 — Fix Podman TLS repair lifecycle

**Verdict: ready to merge.** Small, focused diff (+22/−32 across 4 files) with both changes verified sound:

1. **Shared copy helper.** `Copy-TowerScoutFileIntoContainer` in the TLS CA import script now delegates to the pre-existing shared helper `Copy-TowerScoutContainerPath` in the compose library, deleting the bespoke compose-cp-then-fallback block. Verified: the shared helper sets `$script:TowerScoutComposeExitCode` in both engine branches (direct `podman cp` for Podman, compose `cp` for Docker), so all seven exit-code checks at the import script's call sites keep working and failures still terminate with the correct exit code. Going straight to direct `podman cp` — never attempting `compose cp`, which external Podman Compose providers do not support — removes a known fragile path.
2. **Connection forwarding.** `$env:CONTAINER_CONNECTION` is set only inside the Podman branch of `Get-TowerScoutComposeCommand`, after the rootless connection has been validated. This is the correct variable: external Compose providers launch their own `podman` subprocesses, which honor it, closing the gap where child processes could fall back to a different global default connection. The variable persists for the process afterward, but Docker ignores it and every Podman invocation re-validates and re-sets it, so the persistence is harmless.

Focused regressions cover both behaviors, the automated Codex review completed with zero findings, and the PR records a live end-to-end Podman TLS repair (exit code 0, post-repair readiness `ready`, keyless probe `tls_ok`). No concerns.

## PR #93 — Fix cancellation retry readiness race

**Verdict: ready to merge.** The design is sound: retry readiness is now derived from the actual admission gate (`retryReady = not detection_job_lock.locked()`) on both the `/abort` route and the progress endpoint, instead of being asserted optimistically before the detection slot is actually released. The frontend fails closed — cancellation is resolved only when the progress state is terminal **and** `retryReady === true`, and a successful-but-unparseable abort response now keeps the overlay blocked instead of unlocking an unsafe retry. The existing request-sequence guards prevent stale responses from resurrecting pending state.

Verified details:

- `mark_cancel_requested` returns the *post-mark* state, so replacing the hardcoded `'cancel_requested'` response status with `run_status` preserves the active-run response contract exactly.
- The generated frontend bundle edits match the source edits line for line, and the bundle/source consistency check passed in CI.
- Regression coverage is complete on both sides: backend tests for the terminal-but-slot-still-held window and the progress-endpoint `retryReady` field, frontend contract tests for pending-until-ready, fail-closed non-JSON handling, and stale-response rejection.
- The PR's live validation is convincing: the race was reproduced twice on the frozen rc3 Podman CPU profile (next request rejected with HTTP 429), and the patched build passed the same cancel-then-next smoke twice.

Two behavior changes appear deliberate and correct, and are worth having consciously accepted at merge time:

1. An `/abort` from a session with no run of its own, while the global detection slot is busy, now returns 202/pending instead of 200/ready. The corresponding test was renamed and inverted to codify this. For the process-wide single-slot admission design this is more honest — the old path unlocked the UI into a guaranteed HTTP 429.
2. If a detection thread ever died without releasing the slot, the UI would now stay blocked until restart. That is the pre-existing failure mode made visible rather than a new one.

## PR #91 — docs: record Task-103 rc3 qualification

**Verdict: hold for two reconciliations, then merge after #92 and #93.**

The substance is strong. The first-round automated-review P1 (rc3 digests advancing past the W05 gate without an exact-digest rerun) was addressed the right way — by rerunning all six W05 phases on the exact rc3 CPU and CUDA digests and recording custody identifiers, as reflected in the updated W09 index and accepted by the following review round. The second-round demand to retain every unrun profile workflow as an explicit blocker was honored. A pattern scan of all added lines found no credentials, tokens, local filesystem paths, or personal identifiers.

Two items remain open at the current head:

1. **Unanswered round-3 review finding (P2), posted after the last push.** The W09 evidence index's "Open Acceptance Cells" list (line 190) still states that no real host reboot persistence check has been recorded "for these bytes," while the same PR's W10 index records a four-profile post-reboot persistence check with a real boot boundary as PASS — and the W10 remaining-cells tail (line 400) and the updated task board both count reboot persistence as passed. If the "these bytes" distinction (originally published rc3 package vs. replacement package) is intentional, the line must say so explicitly; as written, the PR contradicts itself.
2. **Evidence describes a cancellation mechanism that exists nowhere in the code.** The W10 index's finding section W10-DCPU-002 (lines 162–171) describes an `/abort` that "waits up to 60 seconds for the shared detection slot" and "returns HTTP 200 with retryReady=true only after the slot is released," with a recorded smoke observing abort HTTP 200 after 7.77 seconds. Neither `main` nor PR #93 contains a bounded server-side wait: #93 returns HTTP 202 immediately when the slot is held and gates the UI on progress polling — its own validation records abort HTTP 202, not 200. The recorded evidence evidently came from an interim local overlay variant of the fix. Since replacement-package re-qualification is already declared mandatory, the light-touch correction is a note in W10-DCPU-002 that the recorded mechanism was an interim overlay, superseded by the implementation merged in #93 and subject to re-validation. Without it, a future operator will read the shipped immediate-202 behavior as a regression against this evidence.

Minor, for record hygiene: the PR description still lists reboot persistence among the "Remaining W10 gates," which the final head's own evidence contradicts. The description was written before the reboot evidence was added in the last commit.

**Dependency note:** the cancel-recovery cells in this evidence presuppose the #93 fix existing in the tree (the recorded flows keep the overlay up until backend-reported readiness). The docs PR should therefore land after the two code PRs, so the repository never records qualification evidence for behavior that does not exist on `main`.

## Cross-cutting observations

- All three PRs correctly state that they publish no packages and promote no image tags — and that boundary is load-bearing: the published rc3 digests were built from `7a5eedd` and contain **neither** fix, so replacement image/package qualification is genuinely required after #92 and #93 merge, before any candidate freeze.
- The W10 finding W10-DCPU-001 (TLS repair helper not preserving a non-default port) is not left dangling by this PR set: `main` already contains that fix via PR #89 (commits `31d3f3a`, `8c5b93d`), which predates the rc3 image source.
- Review coverage: every load-bearing section of #91 (W09 open-acceptance cells, W10 TLS-repair and DCPU finding sections, post-reboot section, remaining-cells tail, task-board hunks) was read directly, alongside all three automated review rounds; the full #92 and #93 diffs were read in their entirety.

## Recommended sequence

1. Merge #92 and #93 (either order; no overlap).
2. On the #91 branch: reconcile the W09 reboot line with the W10 post-reboot evidence, annotate W10-DCPU-002 as an interim-overlay mechanism superseded by #93, and update the PR description's remaining-gates list. Re-request automated review if desired.
3. Merge #91.
4. Proceed to replacement image/package qualification (the remaining W10 gates: unrun profile workflows, controlled-error and review/export cells, managed endpoint policy/signing, independent-host repetition).
