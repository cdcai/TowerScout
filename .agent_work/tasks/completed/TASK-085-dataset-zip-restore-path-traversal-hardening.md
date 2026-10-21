# TASK-085: Dataset ZIP Restore Path Traversal Hardening

**Status**: COMPLETED - source hardening and focused validation passed on June 16, 2026; keep active until sprint closeout
**Priority**: HIGH
**Type**: C (Security / Dataset Restore Hardening)
**Estimated Effort**: 0.5-1 day (4-8 hours)
**Target Sprint**: Sprint 06 V1 RC1 / pre-final-package gate

## Objective

Harden dataset ZIP restore so uploaded dataset archives cannot write files
outside the session temp directory through traversal, absolute paths,
backslashes, drive prefixes, or adapted restore targets that resolve outside
the intended root.

This is a hard pre-final-package gate for the GA/pilot package unless dataset
restore is disabled or explicitly excluded from that package.

## Background

RC5 review found that `/uploaddataset` validates the uploaded ZIP file but did
not validate every ZIP member path before deriving restored file paths and
writing them below `session["tmpdirname"]`.

The route is part of the outbreak-investigation workflow because users can
export a dataset and later restore it for further review. The fix must reject
unsafe archive layouts without breaking valid TowerScout dataset exports.

## Requirements

**R-085-001**: WHEN `/uploaddataset` receives a ZIP archive, THE SYSTEM SHALL
validate every archive member path before it is used for prefix detection,
filename adaptation, or file writes.

**R-085-002**: IF a ZIP member contains `..`, `.`, empty path segments,
absolute paths, backslashes, drive prefixes, scheme prefixes, or null bytes,
THEN THE SYSTEM SHALL reject the upload with a 400 response.

**R-085-003**: WHEN an adapted restore target is produced, THE SYSTEM SHALL
resolve the final path and verify it remains under the current session temp
directory before writing.

**R-085-004**: WHEN an unsafe archive is rejected, THE SYSTEM SHALL avoid
writing files outside the session temp directory and return a support-safe
error message without echoing the raw path.

**R-085-005**: WHEN a valid TowerScout dataset export is restored, THE SYSTEM
SHALL preserve current behavior for `contents.txt`, image files, label files,
session detections, session results, and session metadata.

## Acceptance Criteria

- [x] Dataset ZIP member names are validated before restore processing.
- [x] Traversal, absolute path, drive-prefixed, dot-segment, and backslash
      member names are rejected.
- [x] Adapted restore target paths are resolved and verified under the session
      temp directory before writing.
- [x] Unsafe archives return a 400 response with a support-safe error.
- [x] Valid dataset restore behavior is preserved with regression coverage.
- [x] Focused route tests pass.
- [x] `.agent_work` validation passes.
- [x] `git diff --check` passes.

## Dependencies

- Current `/uploaddataset` route in `webapp/towerscout.py`.
- Existing dataset export/restore route tests.
- `TASK-084` final package sequencing: no final GA/pilot package is published
  until this task is merged and validated unless dataset restore is disabled or
  excluded.

## Implementation Plan

1. Add small dataset ZIP path validation helpers near the restore route.
2. Validate every archive member returned by `ZipFile.namelist()` before old
   stem detection or adapted filename generation.
3. Resolve every adapted write target under the session temp directory and
   verify `os.path.commonpath` stays within the base temp directory.
4. Return a 400 support-safe error for unsafe archive paths.
5. Add route regression tests for traversal and valid restore behavior.
6. Run focused tests and agent-work hygiene validation.

## Non-Goals

- Do not change the dataset export archive structure.
- Do not remove dataset restore from the product.
- Do not refactor detection/session state beyond the restore path safety fix.
- Do not change model, tile, detection, or provider behavior.

## Implementation Log

### 2026-06-16 - Restore Path Safety Implemented
**Objective**: Close the dataset ZIP path traversal gate before final package
publication.
**Context**: `/uploaddataset` restored ZIP members by adapting names and
writing to `tmpdirname + "/" + f_new` without validating each member or the
resolved target path.
**Decision**: Add narrow restore-path helpers in `webapp/towerscout.py` rather
than changing the export format or route contract. Reject unsafe member names
before restore processing and verify resolved write targets stay under the
session temp directory.
**Execution**:
- Added `UnsafeDatasetArchiveError`.
- Added `_validate_dataset_zip_member_name`,
  `_validate_dataset_zip_member_names`, and
  `_resolve_dataset_restore_target`.
- Updated `/uploaddataset` to validate `ZipFile.namelist()` before old-stem
  detection, skip directory entries, and write only to resolved safe targets.
- Added a 400 response path for unsafe dataset ZIP paths.
- Added unit coverage for traversal, absolute path, drive prefix, dot segment,
  backslash rejection, and valid restore behavior.
**Validation**:
- `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py -q -p no:cacheprovider`
  passed with `49 passed`.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\backend\test_endpoint_contract.py -q -p no:cacheprovider`
  passed with `51 passed`.
- `.venv\Scripts\python.exe -m py_compile webapp\towerscout.py` passed.
- `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`
  passed.
- `git diff --check` passed.
**Next**: Commit the completed `TASK-085` slice and return to `TASK-084` final
package publication gates.
