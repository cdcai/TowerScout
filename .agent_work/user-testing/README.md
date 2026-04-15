# User Testing Workspace

This folder keeps user-testing setup and runtime reports organized without mixing raw tester evidence into sprint task files.

## What Lives Here

- `issue-tracker.md`: roll-up view of active and closed user-testing issues
- `artifacts/`: raw screenshots, terminal logs, recordings, and environment notes
- `issues/`: one markdown file per reported problem using the `UT-###` pattern
- `instructions/`: tester-facing reporting instructions and handoff notes

## Workflow

1. Start the tester with one of the existing setup guides under `.agent_work/context/guides/`.
2. When a tester hits a problem, create or update one `UT-###` issue file under `issues/`.
3. Save raw evidence in a dated folder under `artifacts/` and link it from the issue file.
4. Add or update the matching row in `issue-tracker.md`.
5. When engineering work begins, link the issue to the relevant `TASK-###`, branch, PR, or commit.
6. Move the issue through the status lifecycle until the tester confirms the rerun.

## Status Lifecycle

- `NEW`: report received but not reviewed
- `WAITING-FOR-ARTIFACTS`: blocked on logs, screenshots, or environment details
- `TRIAGED`: enough detail exists to route or reproduce the issue
- `IN-PROGRESS`: investigation or fix is underway
- `READY-FOR-RETEST`: change landed and the tester needs to rerun
- `CLOSED`: tester confirmed the issue is resolved or no longer relevant

## Severity

- `BLOCKER`: tester cannot install, launch, or complete the intended test flow
- `HIGH`: core flow works only with a workaround or fails frequently
- `MEDIUM`: partial feature issue with a practical workaround
- `LOW`: minor confusion, polish gap, or non-blocking bug

## Naming Rules

- Issue files: `UT-###-short-slug.md`
- Artifact folders: `YYYY-MM-DD-ut-###-short-slug/`

## Guardrails

- Do not store API keys, full `.env` files, or other secrets in this folder.
- Keep raw artifacts raw. Put analysis and conclusions in the issue file, not the artifact folder.
- Do not close an issue when code or docs change. Close it only after tester retest confirmation.

## Starting Points

- [Issue Tracker](./issue-tracker.md)
- [Instructions](./instructions/README.md)
- [TowerScout User Testing Guide](../context/guides/TowerScout_User_Testing_Guide.txt)
- [TowerScout User Testing Guide - Windows Miniconda](../context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt)
- [TowerScout Development Setup Guide](../context/guides/TowerScout_Development_Setup_Guide.txt)
