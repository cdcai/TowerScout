# TowerScout Codex Skills

Reviewed for handoff on October 20, 2026.

The maintained source is `.agents/skills/` in this repository. Keep it with
the code and open the repository in Codex. Verify that the 12 TowerScout
skills are discovered before relying on them. See the
[manifest](SKILLS_MANIFEST.md) and [maintenance guide](../../maintenance.md).

Do not install a second global copy by default: it can drift from the reviewed
repository procedures. If discovery fails, inspect the installed product's
current documentation and paths before copying anything; preserve existing
personal skills and settings.

Use `towerscout-skill-router` for a task spanning multiple areas. Select one
primary skill and only relevant secondary checks. Skills provide procedures;
they do not prove a test passed or authorize publication.

Official reference: [OpenAI skill guidance](https://learn.chatgpt.com/docs/build-skills).
