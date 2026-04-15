# TASK-049 Stale Surface Archive

**Archived**: 2026-03-31  
**Reason**: Medium-risk stale-surface triage from TASK-049

This archive holds code-adjacent artifacts that were removed from active repo
paths because they are no longer part of the current runtime, build, or pytest
collection flow, but were preserved for historical/debug reference.

## Archived Items

- `js-refactor-helpers/`
  - former `webapp/js/src/comment_providers.sh`
  - former `webapp/js/src/temp_extract_providers.sh`
- `webapp-tests/`
  - former `webapp/tests/` manual diagnostic scripts and HTML harnesses

## Evidence Summary

- `pytest.ini` collects only top-level `tests/`
- `webapp/build.js` does not reference the archived shell helpers
- repo-wide reference searches found no active runtime/build/test references
- the helper scripts depend on outdated TASK-038 Stage 3 line-number extraction
  steps rather than the current modular frontend build

## Restoration

If any archived item is needed again, restore it intentionally from this archive
to an active repo path and revalidate the affected workflow.
