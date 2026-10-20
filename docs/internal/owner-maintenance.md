# Maintaining TowerScout with Codex

**Status:** Handoff draft; practice these steps with Chris before acceptance.

## Start a maintenance task

Open your approved local copy of cdcai/TowerScout in Codex. Confirm the
repository name, selected branch, and any unsaved/uncommitted changes.
Keep the repository's `.agents/skills` with the code; verify discovery in your
installed Codex environment. Do not copy the outgoing maintainer's credentials,
personal settings, or old global skill versions.

Ask:

> Read AGENTS.md and the current task board. Confirm which repository and
> branch are open and preserve existing local changes. Investigate this
> problem: [describe the observed result and expected result]. Choose the
> relevant TowerScout skill, explain the smallest proposed correction, and
> identify how to check it. Do not publish or change repository settings.

## Review a proposed correction

Ask Codex to explain:

1. What changed and which user problem it addresses.
2. What tests actually ran, what passed, and what remains untested.
3. Whether the change affects installation, stored data, providers, models,
   security, or release instructions.
4. How to return safely to the prior version without deleting user data.

Review the diff and evidence before merging. Passing unit tests is not proof
that an installation or model works. Use a separate test installation for
runtime work; preserve existing package folders, project names, and volumes.

## Prepare a future release

> Use the TowerScout release-candidate-gate skill and current accepted
> decisions. Compare the proposed source with the last supported release.
> List the affected checks, exact artifacts to produce, known limitations,
> and any expiring security policy. Prepare a release plan and notes without
> publishing. Do not reuse a release tag for changed bytes.

Only recommend a release after required security, actual-download, and
affected application checks pass. Confirm the exact repository, tag, image
namespace, asset hashes, and authorization before publication.

## Update the wiki

> Review the version-controlled wiki drafts against the current release.
> Propose the smallest documentation correction, check navigation and links,
> and show a preview. Identify the exact wiki destination before publishing.

Keep packaged instructions usable without the wiki or video.

## Review maintenance obligations

> Review TASK-103 and TASK-104 and their accepted decisions. Identify upcoming
> review dates and changes that trigger earlier review. Report evidence and
> recommended next actions; do not extend security exceptions automatically.

The current security exceptions expire October 31, 2026 at 23:59:59 UTC.
The current ML bridge review is due January 31, 2027 or the earlier ADR-022
trigger. These are review obligations, not scheduled automation.

## Skills to keep and additions to consider

Keep the existing 12 TowerScout skills. They already cover release review,
runtime, CI, documentation, model behavior, provider behavior, secrets, and
task tracking. Use the router when the right procedure is unclear.

Two possible future additions are a recurring maintenance review and a wiki
publication checklist. First rehearse the prompts above and the publication
procedure with Chris. Create a new skill only if repeated use exposes a
specific gap; avoid duplicating current release or documentation rules.

Repository-local skills are supported by [OpenAI's skill guidance](https://learn.chatgpt.com/docs/build-skills).
Verify actual availability in Chris's environment during the handoff exercise.
