# Podman Manual Integration

**Date**: October 20, 2026

**Tasks**: TASK-092 / TASK-089; source-document preparation only

## Applied changes

Integrated ADR-026's accepted installation restrictions into eight maintained
documentation files: Quick Start Markdown/HTML, Podman CPU/GPU guides, advanced
package guide, Local IT Markdown/HTML, and the support OCI quick start.

- Require a package-root path of 80 characters or fewer, with short PC/PG
  extraction examples and a PowerShell path-length check.
- Explain that this is a conservative operating restriction, not a universal
  Windows limit or a guarantee. Preserve existing installation identities and
  volumes; arrange relocation with support rather than moving configured folders.
- Select 64-bit Python 3.12 explicitly and pass its executable through the
  existing `-Python` option. Verify version/bitness; stop on errors or mismatches.
- Cover missing Python-launcher selection through an approved executable path.
- Correct the support guide's blanket claim that package users need no Python.

The Quick Start and Local IT HTML are maintained separately; no canonical
Markdown-to-HTML generator was identified. Both formats were edited directly.
The Quick Start command examples were compared for parity.

## Review finding corrected

The unsigned-support documentation test caught a regression from the earlier
organization pass: `.agent_work/README.md` referenced the decision range but
no longer directly named ADR-023 or the unsigned support boundary. Restored
the direct decision link and boundary statement without changing that policy.

## Validation

- 21 existing documentation/unsigned-support tests passed.
- Used `--noconftest -o addopts= -p no:cacheprovider` for these fixture-free
  text tests. The initial normal invocation stopped before collection because
  shared conftest tried to create runtime directories in the restricted worktree.
- Existing headless Edge layout check passed at 1440px and 720px. The initial
  sandbox launch returned EPERM; the approved local browser run succeeded.
- Added local file links and heading anchors resolve; Quick Start HTML IDs
  are unique and the new command lines match Markdown.
- The read-only Python version/bitness command returned Python 3.12.10, 64-bit
  on this host. No provider installation or runtime mutation was executed.
- Strict agent-work validator and whitespace checks passed.

## Still pending

The maintained source now includes the restrictions, but no release ZIP or
image was rebuilt. Immutable RC5 artifacts and their separate supplement are
unchanged. Verify these instructions inside the actual official package and
served Help during official qualification. Task-092 remains in progress.

Next review official destination/default references, wiki consistency and
remaining adoption content. Do not replace historical fork provenance or
invent official downloads before publication. No remote action occurred.
