# PR #113 dependency and adoption review

**Date:** October 21, 2026. **Tasks:** TASK-104 / TASK-089 / TASK-105.
**Current status:** owner approval was explicitly supplied in the conversation:
"Alright, I approve PR 113." Exact head `2980f96` was rechecked and squash-merged
to the fork as `60ae1c9b78499d033eddfd09cb663622c17287b3` at 17:04 UTC on
October 21. The merge tree is identical to the approved PR tree. Integration
commit `8b49f74` preserves fork-main ancestry and the two rehearsed documentation
resolutions. Application, tests, scripts, configuration and agent skills match
rehearsal `292ed93`; later differences are review/status documents only.
No GitHub review is fabricated; the explicit conversational owner approval is
the approval record. cdcai source adoption and official qualification remain open.

The detailed results below retain their pre-merge recording context. The final
PR descriptions and local execution receipt record subsequent remote checks.

## Reviewed correction

[PR #113](https://github.com/J-Schulein/TowerScout/pull/113), head
`2980f96c6c9467b20a050f05a889a894853a65cd`, contains eight changed files:
aiohttp 3.14.3 to 3.14.4, Pillow 12.3.0 to 13.0.0, the matching Pillow runtime
minimum, three existing test contracts, one agent instruction and task evidence.
The aiohttp correction addresses alerts 77/78/79 (two High, one Low).
The first corrected-head scan exposed seven existing Pillow findings (one
Critical, six High); the separately committed Pillow correction clears the
blocking source scan. No exception, scanner baseline, model weight, threshold,
torch/torchvision pin or publication workflow was changed.

The original full-image job was skipped because PR events do not satisfy its
main-only condition. It is not a required PR build that was omitted by accident.

## Validation and observed limits

- [Final CI](https://github.com/J-Schulein/TowerScout/actions/runs/39638117871):
  Python 3.11 and 3.12 each report 586 unit tests passed, 161 skipped and five
  subtests passed. The blocking High/Critical security scan, frontend tests
  and Docker frontend stage pass. The main-only full-image job is skipped.
- [Maintained controller checks](https://github.com/J-Schulein/TowerScout/actions/runs/39638118179):
  controller contracts, simulated-helper end-to-end and Windows contracts pass.
  This does not resume deferred launcher development.
- Advisory integration reports five failures, 18 passes, three skips and one
  subtest pass on each Python version. The same failure summary occurred on
  the aiohttp-only head before Pillow changed. A subsequent comparison with
  accepted-main CI run 39293707555 confirmed the same four failed test cases
  and radius subtest before either update. Black, mypy and Bandit also
  retain advisory failures in the raw logs; successful job labels do not mean
  every advisory command passed. No controls were relaxed.
- Local resolved aiohttp set: 21 focused provider/redaction tests passed.
  aiohttp now requires yarl >=1.25.1; the isolated resolved set uses 1.25.1.
- Local combined dependencies: 68 focused upload, allocation/admission,
  provider, loader and classifier tests passed.
- Synthetic preprocessing comparison: all five JPEG/PNG RGB, grayscale,
  palette and alpha cases produced identical crop/RGB/resize/tensor output
  hashes between Pillow 12.3.0 and 13.0.0 using the maintained transform.
- Rehearsed adoption integration: the first combined run had 143 passes and
  one Windows connection reset in the unchanged Waitress oversized-request
  test. Its focused rerun passed; the full repeat passed all 144 tests in
  29.90 seconds. Retain the initial failure as an observed transient, not a
  proven root-cause resolution. No assertion was relaxed.
- Local tests used Python 3.12 and torch/torchvision 2.6.0+cpu/0.21.0+cpu;
  remote CI installs the maintained 2.10.0/0.25.0 pair. Model loading in pytest
  is mocked. No new real-model, CPU/CUDA or official-byte qualification is claimed.

## Integration rehearsal

The rehearsal combines preparation checkpoint `d1c55ad` and PR head `2980f96`
in an isolated worktree. The only conflicts were the agent instruction and
TASK-104 status document. Preserve the newer adoption guidance and historical
status separation, then add the dependency follow-up explicitly. Runtime and
test changes merged without conflict. Recheck these resolutions when merging
the actual accepted fork-main commit; the rehearsal is not that acceptance.

Original local documentation, immutable RC5 artifacts, security exceptions,
deferred branches and cdcai source remain unchanged. No merge, cdcai PR,
official build, image/release publication or wiki write occurred in this slice.

## Sequence recorded before owner approval

1. Obtain the required review approval for the concrete eight-file PR above.
   The repository management policy requires one approval; GitHub currently
   has no submitted review. Do not manufacture an owner approval or treat
   absent branch protection as a waiver.
2. Recheck the exact PR head/base/checks, squash-merge to the fork, retain the
   branch/evidence and verify post-merge CI plus dependency-alert refresh.
3. Merge accepted fork main into the preparation branch, apply the rehearsed
   documentation resolutions, verify the tree and refresh this receipt.
4. Push the reviewed preparation branch to the fork and run PR-based remote
   checks before the cdcai adoption merge. Branch push alone does not run CI.
5. Qualify official images/packages with fresh scans and resolved inventories,
   image decode/preprocessing, both model/device paths, providers, cancellation,
   recovery and the existing two-host matrix. Prior unchanged-runtime wording
   does not apply to the new dependency delta. Do not renew ADR-024 exceptions.

Detailed local receipts are under output/handoff/pr113-evidence in the original
workspace, with the preprocessing comparison and both integration test reports
alongside it. These are source-review receipts, not a new release acceptance.
