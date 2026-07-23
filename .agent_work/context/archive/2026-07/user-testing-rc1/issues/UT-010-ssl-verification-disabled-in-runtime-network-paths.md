# UT-010: SSL Verification Is Disabled In Multiple Runtime Network Paths

**Status**: READY-FOR-RETEST
**Severity**: BLOCKER
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The original TLS-verification concern was valid when this issue was opened, but the active runtime contract has since changed. On commit `a2160dc`, TLS verification is now on by default across the touched runtime paths, and the only remaining bypass behavior is an explicit opt-in escape hatch via `TOWERSCOUT_ALLOW_INSECURE_TLS`. This issue should stay open only long enough to confirm that the secure-default behavior holds in the next clean smoke or user rerun.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: Google and Azure
- GPU or CPU path: not relevant

## Reproduction

1. Inspect the map-download, geocoding, and config-validation request code.
2. Confirm that the earlier global SSL overrides are gone.
3. Confirm that insecure TLS is only enabled when `TOWERSCOUT_ALLOW_INSECURE_TLS` is set.

## Expected Result

TowerScout should verify TLS certificates by default. Any development-only bypass should be narrowly scoped, explicit, and opt-in rather than globally disabling certificate verification.

## Actual Result

The current code now shows a narrower, explicit contract:

- `webapp/ts_maps.py` uses `ssl=False` only when `TOWERSCOUT_ALLOW_INSECURE_TLS` is enabled
- `webapp/ts_geocoding.py` uses `verify=self.verify_tls` instead of hard-coded `verify=False`
- `webapp/ts_config.py` only bypasses verification inside `_validation_get()` when `TOWERSCOUT_ALLOW_INSECURE_TLS` is enabled
- the earlier global `ssl._create_default_https_context` overrides are gone

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/ts_maps.py`
  - `webapp/ts_geocoding.py`
  - `webapp/ts_config.py`

## Triage Notes

- This captures senior engineer critique item 4.
- The senior review on April 13 correctly marked this as resolved in the active runtime.
- The current bypass is explicit and environment-gated rather than silent and global.
- A clean retest is still worthwhile because the setup/config validation path retains an intentional insecure-TLS branch when the env flag is enabled.

## Retest Notes

- Retest owner: future implementer
- Retest date: pending
- Retest result: pending

## Resolution

Engineering review on April 14, 2026 found that commit `a2160dc` resolves the original secure-default issue. Keep this in `READY-FOR-RETEST` until the next clean smoke or user rerun confirms that TowerScout works without needing the insecure-TLS escape hatch.
