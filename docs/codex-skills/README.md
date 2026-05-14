# TowerScout Codex Skills

Updated package generated 2026-05-14.

## Install location

For repository-scoped use, copy the `.agents` directory into the TowerScout repository root:

```text
TowerScout/
  .agents/
    skills/
      towerscout-skill-router/
      towerscout-release-candidate-gate/
      ...
```

Some Codex builds can discover repository-scoped skills from `.agents/skills` by scanning from the current working directory up to the repository root. Launch Codex from the TowerScout repo root or a folder inside that repository, then verify the skills are visible before relying on implicit routing.

If repo-scoped discovery is not available in the active Codex build, copy the skill folders to `$CODEX_HOME/skills`. When `CODEX_HOME` is not set, use `~/.codex/skills`. This is the confirmed fallback location for the current TowerScout Codex environment.

## Discovery troubleshooting

1. Confirm each skill has `.agents/skills/<skill-name>/SKILL.md`, or `<skills-root>/<skill-name>/SKILL.md` when installed through `$CODEX_HOME/skills` or `~/.codex/skills`.
2. Start Codex from the TowerScout repo root or a subfolder inside it.
3. Use `/skills` or type `$` to check whether the skills are visible.
4. Restart Codex if newly copied or updated skills do not appear.
5. If the initial skills list is crowded, Codex may shorten or omit some descriptions; invoke a skill explicitly with `$skill-name`.

## Routing model

Use `towerscout-skill-router` when a task spans multiple areas. Otherwise choose one primary skill and add only focused secondary checks. Release-related skills intentionally overlap less now: release gate is for whole-package RC validation; compliance is for license/notice/source artifacts; container runtime is for Docker/Podman/launcher files; end-user docs is for user-facing docs; secret safety is for keys/artifacts/logs.

See `SKILLS_MANIFEST.md` for the full table.
