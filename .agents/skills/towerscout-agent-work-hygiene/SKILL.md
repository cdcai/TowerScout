---
name: towerscout-agent-work-hygiene
description: Maintain concise sanitized task and evidence summaries for TowerScout changes.
---

# TowerScout task and evidence hygiene

Read `AGENTS.md`, `docs/maintenance.md` and `CONTRIBUTING.md`.
Use this skill for change records, PR evidence summaries and maintenance handoff.
Keep one current issue/PR checklist and a sanitized evidence index. Record source, artifact identities,
actual results, limitations and the next owner/action. Deferred work remains deferred.
Keep private working records and raw runtime/browser evidence outside public commits.
Use repository issue/PR references rather than mandatory private archive paths.
Run the relevant checks for the touched area; do not claim deployment readiness from static or mocked tests.
Use the quick checker below to verify the public maintenance entrypoints:

```bash
python .agents/skills/towerscout-agent-work-hygiene/scripts/check_agent_work_quick.py .
```

Report changed guidance, missing public references, validation results and any remaining owner dependency.
