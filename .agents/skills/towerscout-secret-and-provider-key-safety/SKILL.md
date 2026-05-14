---
name: towerscout-secret-and-provider-key-safety
description: 'Primary skill for TowerScout secret-safety work: provider keys, setup/settings
  config, .env handling, log/error sanitization, screenshots, browser artifacts, support
  diagnostics, and release evidence. Use as a secondary PR safety check when artifacts
  or evidence are touched.'
---

# TowerScout Secret and Provider Key Safety

Use this skill when code or docs touch API keys, provider configuration, Setup Wizard, settings, `.env` files, logs, errors, browser artifacts, screenshots, network traces, release packages, or support diagnostics.

## Goal

Prevent secrets and sensitive investigation details from being committed, logged, packaged, or exposed through avoidable error messages.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for secret/config/logging changes. Use it as a secondary safety check on PRs that include browser artifacts, support evidence, release evidence, or setup/settings changes.

## First read

- `AGENTS.md/security.md`
- `.github/copilot-instructions.md` security sections
- `webapp/ts_config.py`
- `webapp/ts_logging.py`
- `webapp/ts_errors.py`
- `webapp/ts_validation.py`
- `tests/unit/test_config.py`
- `tests/unit/test_error_sanitization.py`

## Review checklist

1. Do not commit `.env`, local fixtures with sensitive AOIs, raw browser artifacts, raw logs, screenshots, provider responses, or API keys.
2. Google and Azure browser SDK keys may be client-visible by provider design, but docs should explain restrictions/support policy when needed.
3. Server responses should mask key previews.
4. Setup/settings logs should not print full keys.
5. Provider validation failures should be actionable without dumping provider response bodies or keys.
6. Release packages should not include local config, sessions, logs, uploads, temp files, caches, or browser-run artifacts.

## Inspect commands (read-only)

```bash
git diff --cached
git diff
python .agents/skills/towerscout-secret-and-provider-key-safety/scripts/scan_for_sensitive_terms.py
```

The default source-tree scan skips generated package/build output such as `dist/` and `build/`. When reviewing a release artifact, pass the package directory or extracted ZIP root explicitly:

```bash
python .agents/skills/towerscout-secret-and-provider-key-safety/scripts/scan_for_sensitive_terms.py dist/<package-dir-or-extracted-zip>
```

## Build/update generated files (mutating)

No standard mutating command. Do not create or copy real `.env` files or raw support artifacts into tracked paths.

## Validation commands

```bash
python -m pytest tests/unit/test_config.py tests/unit/test_error_sanitization.py tests/unit/test_flask_routes.py -q -p no:cacheprovider
```

## Output format

Return sensitive surfaces touched, possible leaks found, redaction/masking changes made or recommended, tests run, and residual provider-key policy questions.
