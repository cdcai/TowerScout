---
name: towerscout-ci-quality-ratchet
description: 'Primary skill for TowerScout CI workflow and quality-gate changes: GitHub
  Actions, continue-on-error policy, lint/type/security checks, Node/Python version
  upgrades, action pins, coverage, and incremental gate tightening. Separates inspect-only
  review from mutating validation commands.'
---

# TowerScout CI Quality Ratchet

Use this skill when a task changes `.github/workflows/*`, `requirements-dev.txt`, lint/type/security settings, test gates, action pins, Node/Python versions, coverage, or release CI gates.

## Goal

Improve CI quality without causing broad unrelated churn or making unstable checks block urgent release work prematurely.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Strategy

Prefer small, reversible ratchets:

1. Make one focused check stricter at a time.
2. Start with changed files or release-critical surfaces when whole-repo drift is large.
3. Keep advisory checks advisory until there is evidence they are stable.
4. Record why a check remains `continue-on-error` or why it becomes blocking.
5. Avoid drive-by formatting of the whole repo unless explicitly planned.

## First read

- `.github/workflows/ci.yml`
- `.github/workflows/container-publish.yml`
- `requirements-dev.txt`
- `pytest.ini`
- `package.json`
- `package-lock.json`
- `.agent_work/current-tasks.md`

## Review checklist

1. Minimal permissions per job.
2. Expected branch and PR triggers.
3. Manual publish workflows require explicit inputs.
4. GitHub Actions refs follow repo policy.
5. Node/Python upgrades are validated against build, Puppeteer, and runtime paths.
6. `continue-on-error` is justified for unstable or historical-drift checks.
7. Release-critical checks are candidates for blocking status.
8. Artifact upload does not include secrets, raw provider outputs, or excessive generated files.

## Inspect commands (read-only)

```bash
python .agents/skills/towerscout-ci-quality-ratchet/scripts/summarize_ci_workflow.py .github/workflows/ci.yml
python .agents/skills/towerscout-ci-quality-ratchet/scripts/summarize_ci_workflow.py .github/workflows/container-publish.yml
git diff -- .github/workflows requirements-dev.txt pytest.ini package.json package-lock.json
```

## Build/update generated files (mutating)

No standard mutating command. Do not reformat the repo or regenerate lockfiles unless the task explicitly asks for that ratchet.

## Validation commands

Choose the smallest set needed for the proposed ratchet.

```bash
python -m pytest tests/unit -q -p no:cacheprovider
flake8 webapp/ --count --select=E9,F63,F7,F82 --show-source --statistics
black --check --diff webapp/
mypy webapp/ --ignore-missing-imports --no-strict-optional
bandit -r webapp/
node webapp/build.js
node tests/integration/test_task_064_provider_state_manager.js
```

## Output format

Return proposed ratchet, why it is safe now, current failures or drift, checks that remain advisory and why, commands run, and follow-up ratchets.
