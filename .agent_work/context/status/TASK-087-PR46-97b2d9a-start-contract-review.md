# Task-087 / PR #46 review at `97b2d9a`

## Review verdict

The `97b2d9a` browser start-contract checkpoint is acceptable as a **non-mutating Gate 3 proof** before wiring the live helper POST/poll flow. I do not see a blocker to proceed to the next focused implementation checkpoint, provided the next checkpoint is still reviewed before any live browser-triggered host mutation is enabled.

PR #46 is open, mergeable, and draft at head SHA `97b2d9a79a7b6bb35ca212dfaee96aa3fe1cad40`. Its stated safety boundaries remain: no enabled/actionable repair button, no browser-triggered host mutation, `provider_tls_repair=true` disabled, Podman remediation blocked, and tester-facing package inclusion blocked. fileciteturn274file0L4-L14

This remains consistent with the Task-087 Gate 3 model: product integration must prove the repair action appears only for repairable TLS trust categories, preserves structured provider failures, treats helper-unavailable as fallback, and prevents token/credential leakage before moving toward user-facing package inclusion. fileciteturn273file0

## Start-contract shape

The start-contract shape is appropriately narrow. The Setup Wizard defines the provider TLS repair endpoint as `/operations/provider-tls-repair`, the fixed confirmation as `repair_tls_and_restart`, and the only allowed request-body fields as `provider`, `confirmation`, and `operation_authorization`. It separately enumerates disallowed fields such as command/script/runtime/restart/Podman/helper-token fields. fileciteturn276file0L18-L44

The contract preview returns only a sanitized schema: endpoint, method, content type, provider enum, fixed confirmation, allowed/disallowed field names, and a redacted operation authorization summary. It does not include the raw operation token in the preview. fileciteturn277file0L151-L204

The internal request builder, which is not yet reached because browser mutation is disabled, would construct only `provider`, fixed `confirmation`, and `operation_authorization`. It does not include engine, GPU, port, command paths, restart mode, Podman provider fields, helper token, or arbitrary arguments. fileciteturn277file0L206-L226

## Non-mutating behavior

The non-mutating boundary still holds. `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED` remains `false`; the view model enables repair only when authorization is current and that mutation gate is open. Because the gate is closed, even a valid authorization leaves the action disabled with `browser_mutation_disabled`. fileciteturn276file0L18-L22 fileciteturn277file0L127-L148

`startProviderTlsRepair()` does not start a helper operation. It returns `false` for invisible, active-operation, disabled, already-starting, and stale-authorization states. In the final gated branch, it only shows an informational notification saying execution is still pending review, then returns `false`. fileciteturn278file0L57-L107

The host helper capability also remains disabled: the helper runtime profile still reports `provider_tls_repair = false` and `podman_provider_repair = false`. fileciteturn285file0L12-L27

## Redaction and active-operation handling

Operation authorization redaction is handled correctly for this checkpoint. The internal validation record may hold the short-lived token, but public validation-state cloning removes `operation_token`, keeping only `operation_type` and `expires_at`. The contract summary also replaces the raw token with the placeholder `short_lived_operation_authorization`. fileciteturn276file0L162-L175 fileciteturn277file0L104-L114

Active operation status is sanitized before it is remembered. The normalizer accepts only provider enum, operation type, operation id format, allowlisted classification/next-action symbols, booleans, current step, and public operation state. It drops runtime details, helper tokens, command paths, and other unrecognized fields. fileciteturn277file0L43-L77

The active-operation behavior is also reasonable for the non-mutating checkpoint. Non-terminal `pending`, `active`, and `intermediate_success` statuses block a new start contract as `operation_active`; terminal status clears active-operation blocking and returns to the normal gated state. fileciteturn277file0L79-L102

## Test coverage

The contract tests cover the right start-contract boundary. With a valid short-lived authorization, they verify endpoint, method, content type, provider, fixed confirmation, allowed body fields, request-body schema, redacted authorization summary, and absence of the raw token from the contract. They also assert forbidden runtime/control fields are not allowed. fileciteturn282file0L74-L116

The tests verify duplicate clicks while mutation is disabled do not launch repair and that rendered panel text, notifications, and console output do not include the operation token. They also verify fetch calls remain only the provider validations, `google` and `azure`. fileciteturn282file0L118-L140

The active-operation test simulates an `operation_busy` status containing a durable helper token, command path, and runtime fields. The remembered/public status drops those sensitive fields, the start contract becomes `operation_active`, notifications stay token-safe, and no helper request is issued. It also verifies terminal `ready` status clears the active-operation block. fileciteturn282file0L143-L229 fileciteturn283file0L1-L10

Expired, malformed, wrong-type, missing-token, and non-object authorization inputs remain covered from the prior checkpoint: they leave the panel disabled, report authorization unavailable, do not start repair, and do not expose token text in public state or rendered DOM. fileciteturn283file0L12-L128

The PR currently has no review comments returned. fileciteturn284file0L1-L3

## Boundary confirmation

No real browser-to-helper operation start is enabled yet. The code defines a contract preview and a private request builder, but `startProviderTlsRepair()` still returns `false` and does not call `fetch` for the helper operation. fileciteturn278file0L57-L107

No runtime/control fields are sent by the contract. The only eventual request-body fields are provider enum, fixed confirmation, and short-lived operation authorization. The start-contract tests also assert runtime/control/Podman/helper-token fields are not in the allowed body fields. fileciteturn277file0L206-L226 fileciteturn282file0L98-L116

`provider_tls_repair=true` remains disabled, Podman remediation remains blocked, and tester-facing package inclusion remains blocked. The PR body states those boundaries, and the helper runtime profile still advertises both repair capabilities as false. fileciteturn274file0L8-L8 fileciteturn285file0L21-L24

## Feedback classification

### Blocker before live POST/poll wiring design

None. This checkpoint is sufficient before wiring the live helper POST/poll flow.

### Should fix before enabling real browser-triggered mutation

The next checkpoint should add the actual live POST/poll implementation behind tests, but keep it disabled until review. The tests should prove that the browser sends exactly the body shape already defined here and that no console/DOM/status/notification surface leaks operation tokens, helper tokens, command paths, runtime values, or raw helper responses.

Add a focused test for helper-unavailable during the start attempt itself. The current tests cover helper-unavailable validation states and active/busy restored status. The live start flow should also prove that a failed helper availability check or failed operation POST degrades to command fallback without mutation retry loops.

Add explicit reload/reconnect tests once polling exists. The current active-operation memory path is a good local simulation, but the real flow must prove page reload can recover by polling status/readiness rather than starting a second operation.

### Blocker before user-facing enablement

User-facing enablement remains blocked until the live browser-to-helper POST/poll flow passes review, reconnect behavior survives restart, package/support-artifact exclusions are proven, and managed-network package validation passes. Do not enable an actionable repair button, do not set `provider_tls_repair=true`, do not expose Podman remediation, and do not include this in tester-facing packages yet.

### Follow-up acceptable after this gate

Helper-unavailable/manual fallback copy can continue to be refined while still non-mutating.

CUDA/CUDA-package validation, managed-network package validation, package exclusion tests, and Podman remediation remain later gates.

## Recommendation

Proceed to the live browser-to-helper POST/poll design checkpoint.

The `97b2d9a` slice defines the right start contract, keeps the browser non-mutating, limits the future body to provider enum plus fixed confirmation plus scoped operation authorization, redacts operation/helper tokens and runtime/control fields from public state, and handles helper-unavailable, expired authorization, duplicate clicks, active operation/reload-style status restoration, and `operation_busy` without launching repair. The next checkpoint should review the actual POST/poll implementation before any mutation path is enabled.
