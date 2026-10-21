# Security follow-up for Chris - discussion draft

## What needs attention

The accepted candidate has five narrowly defined exceptions for security
scanner findings in included dependencies. The project recorded reasons and
limits for accepting those exact findings temporarily. This is not a claim
that every future build is safe or that those findings can be ignored.

The exceptions expire **October 31, 2026 at 23:59:59 UTC**. Expiry does not
turn off installed TowerScout copies. It ends the current publication-policy
acceptance: we cannot rely on it to pass a new release gate after expiry.
Do not disable checks or simply move the expiry date to make a build pass.

## Proposed action before support ends October 30

1. Outgoing lead/Codex: run fresh checks for the official CPU and CUDA builds.
   Compare exact findings against TASK-104, ADR-024 and the residual policy.
2. For available fixes: prepare the smallest dependency correction, rebuild,
   remove resolved exceptions as appropriate, and run affected checks.
3. If a fix is unavailable: explain the exact remaining finding, supported
   application exposure, alternatives and uncertainty to Chris. Seek technical
   security help where needed; do not infer safety from a prior acceptance.
4. Chris: review the evidence and decide on the next action. Any continued
   exception requires a new explicit written decision with scope, rationale,
   owner and review/expiry date, subject to organizational policy. If there is
   no valid decision or a required gate fails, hold the affected publication.
5. Outgoing lead: deliver the final status, evidence links, outstanding actions
   and dates. Chris: confirm he can locate these and explain the next step.

This is a proposed responsibility split, not a record that Chris has already
approved it. His general awareness is recorded separately from understanding
and a specific decision. Resolve or clearly assign follow-up before October 30;
do not leave the first review until October 31.

## Prompt Chris can use with Codex

> Read TASK-104, ADR-024 and .github/security/task103-accepted-residuals.v1.json.
> Explain the current findings and deadlines in plain language. Identify the
> exact build and scan evidence needed to assess available fixes. Prepare a
> proposed action plan without publishing, changing exceptions or weakening
> checks. Separate verified facts from assumptions and identify where expert
> security review is needed.

This brief summarizes existing project decisions; it is not a fresh scan or
an assessment of whether upstream fixes are currently available.
