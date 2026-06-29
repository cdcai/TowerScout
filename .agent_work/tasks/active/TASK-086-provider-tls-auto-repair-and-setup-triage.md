# TASK-086: Provider TLS Auto-Repair And Setup Triage

**Status**: COMPLETED - V3 CPU managed-network proof passed and owner-confirmed CUDA managed-network validation shows the Task-086 TLS repair fix works for the CUDA package path; keep Task-087 as a follow-on one-click helper plan, not an rc7 baseline blocker
**Priority**: HIGH
**Type**: B/C (Runtime Support / Provider Setup / TLS Trust)
**Estimated Effort**: 3-5 days (24-40 hours) plus one managed-network validation pass
**Target Sprint**: Sprint 06 post-RC6 UAT follow-up / next pilot package

## Objective

Reduce first-run provider setup friction on managed networks by adding a guided
TLS inspection CA diagnosis and repair path for Google Maps and Azure Maps,
centralizing provider HTTP/TLS handling, and improving Setup Wizard triage,
while preserving TowerScout's default secure TLS verification posture.

This task should make the already-validated `scripts/import-tls-ca.cmd` repair
path easier and safer to execute. It should not replace TLS verification, move
provider traffic to a new host-side proxy, or import trust anchors without
explicit user/support action.

The repair flow should address both the support command and the product
surfaces that report the failure. Provider validation, geocoding, map proxy,
static imagery, tile, and search calls should not diverge in how they validate
TLS, classify provider errors, or redact secrets.

## Background

UAT feedback reproduced a Google Maps setup failure where the provider key was
believed to be correct, but container-side validation failed with TLS
certificate verification errors. Prior validation confirmed the same failure
mode can be resolved by importing the local managed-network TLS inspection CA
into the selected Docker stack. This makes the problem a supportability gap in
container trust setup, not a Google key defect.

Current TowerScout behavior:

- Provider validation and runtime provider calls run inside the Linux
  container.
- The container uses its own CA bundle and does not automatically inherit the
  Windows enterprise certificate store.
- `scripts/import-tls-ca.cmd` can import a selected Windows CA certificate into
  the selected Docker or Podman config volume, build
  `/app/webapp/config/certs/towerscout-ca-bundle.pem`, update `.env`, and verify
  provider TLS with an intentionally invalid provider key.
- The hard part for non-technical users and first-line support is identifying
  the correct Windows certificate thumbprint without importing a website leaf
  certificate or trusting the wrong certificate.

Supporting analysis:

- `.agent_work/context/analysis/GOOGLE-MAPS-TLS-CA-TRUST-ANALYSIS-2026-06-26.md`
- Teammate repair-helper proposal reviewed on 2026-06-26. The useful direction
  is dry-run discovery plus explicit apply semantics that reuse
  `scripts/import-tls-ca.cmd`; the prototype needs GPU-mode forwarding,
  stronger certificate-selection checks, and support-safe output before it is
  productized.
- Reviewer feedback on 2026-06-26 recommended accepting the CA-import model but
  adding a shared provider HTTP/TLS wrapper, container-side no-key TLS preflight,
  structured Setup Wizard statuses, and explicit Azure-success/Google-repair
  behavior so this becomes a product workflow instead of only a support
  workaround.
- Follow-up reviewer analysis on 2026-06-26 approved the plan direction after
  targeted refinements: explicitly include `webapp/ts_maps.py` async imagery
  downloads, remove provider response-body snippets from the low-level import
  helper, define no-key TLS preflight success semantics, make certificate
  candidate scoring deterministic and conservative, clarify repair-pending key
  persistence, keep `/api/config/tls-status` read-only/container-scoped, and
  raise the estimate for the full hardening scope.
- Updated reviewer feedback on 2026-06-26 approved the expanded plan and
  recommended one additional explicit requirement: successful detection
  results, session state, exports, support artifacts, and UI-facing tile
  records must not expose credential-bearing provider URLs.

## Requirements

**R-086-001**: WHEN provider validation fails because of TLS certificate
verification, THE SYSTEM SHALL continue to report an actionable support-safe
message rather than a generic provider-validation failure.

**R-086-002**: WHEN support runs the provider TLS repair helper without apply
semantics, THE HELPER SHALL inspect the selected provider host's TLS chain,
identify safe candidate trust anchors, print a recommended repair command, and
make no filesystem, `.env`, container, or volume changes.

**R-086-003**: WHEN the helper selects a candidate automatically, THE HELPER
SHALL NOT select the leaf website certificate.

**R-086-004**: WHEN the helper selects a candidate automatically, THE HELPER
SHALL require evidence that the candidate is a CA certificate and is suitable as
a trust anchor or chain-building intermediate.

**R-086-005**: WHEN the helper can resolve a candidate by thumbprint, THE HELPER
SHALL prefer certificates found in the Windows `CurrentUser` or `LocalMachine`
Root/CA stores over certificates observed only on the wire.

**R-086-006**: IF no safe candidate can be identified, THEN THE HELPER SHALL
stop without importing anything and print a support action that asks local IT
for the organization proxy/root/intermediate CA thumbprint or certificate file.

**R-086-007**: WHEN support supplies `-Thumbprint` or `-CertificatePath`
manually, THE HELPER SHALL pass the explicit selection through to the existing
import helper after validating that exactly one selection mode was provided.

**R-086-008**: WHEN the helper applies a repair, THE HELPER SHALL reuse
`scripts/import-tls-ca.cmd` for the container copy, bundle construction,
provider TLS verification, and `.env` update.

**R-086-009**: WHEN the helper calls `scripts/import-tls-ca.cmd`, THE HELPER
SHALL forward `-Engine`, `-Gpu`, and `-VerifyProvider` so CPU, Docker GPU,
Podman CPU, and Podman GPU support paths use the same runtime profile selected
for launch.

**R-086-010**: WHEN Docker and Podman are both used on the same workstation, THE
SYSTEM SHALL keep the repair engine-scoped and make clear that each engine has
its own config volume.

**R-086-011**: WHEN the helper prints diagnostics, THE HELPER SHALL avoid
printing provider keys, full provider URLs containing keys, raw HTTP response
bodies, or raw network traces.

**R-086-012**: WHEN diagnostic output includes certificate identity details, THE
HELPER SHALL keep the output concise enough for support triage and avoid
creating public-release evidence that includes organization-specific certificate
names or thumbprints.

**R-086-013**: WHEN Setup Wizard or Settings receives a structured provider TLS
failure, THE UI SHALL distinguish TLS trust problems from invalid provider-key
problems and point to the provider TLS repair helper.

**R-086-014**: WHEN bootstrap or setup support output reports a provider TLS
trust issue, THE OUTPUT SHALL include the selected engine and GPU-mode context
needed to run the repair helper correctly.

**R-086-015**: WHEN the repair helper is included in a release package, THE
PACKAGE SHALL include both `.ps1` and `.cmd` entry points and package tests
shall verify they are included.

**R-086-016**: WHEN TowerScout makes provider HTTP calls for validation,
geocoding, map proxy, static imagery, tile, or search workflows, THE SYSTEM
SHALL route those calls through a shared provider HTTP/TLS helper or documented
adapter that centralizes TLS verification, configured CA bundle validation,
timeouts, provider labels, structured failure categories, and redacted logging.

**R-086-017**: WHEN provider HTTP/TLS failures are classified, THE SYSTEM SHALL
emit stable support-safe categories for at least `tls_ca_untrusted`,
`tls_bundle_missing`, `tls_bundle_unusable`, `provider_timeout`,
`provider_network_blocked`, `provider_http_error`, `invalid_provider_key`, and
`provider_api_not_authorized`.

**R-086-018**: WHEN bootstrap, setup, or support preflight checks provider TLS
readiness, THE SYSTEM SHALL probe the selected engine/container path without
requiring a real provider key and distinguish TLS trust failures from blocked
network, DNS, timeout, and provider HTTP failures.

**R-086-019**: IF container-side preflight indicates the provider endpoint is
blocked or unreachable for reasons unrelated to CA trust, THEN THE SYSTEM
SHALL avoid suggesting CA import as the primary fix and shall report a
managed-network allowlisting/support action instead.

**R-086-020**: WHEN Setup Wizard or Settings displays provider validation
state, THE UI SHALL preserve structured status values including `not_entered`,
`valid`, `invalid_key`, `api_not_authorized`, `tls_untrusted`,
`tls_bundle_missing`, `tls_bundle_unusable`, `network_blocked`, `timeout`, and
`unknown_error`, or a directly mapped equivalent.

**R-086-021**: WHEN frontend provider validation receives structured backend
details, THE UI SHALL preserve the category, provider, and support-safe detail
instead of flattening the response into a generic `Error.message`.

**R-086-022**: WHEN Azure validation succeeds and Google has a TLS repairable
failure, THE UI SHALL allow a valid Azure configuration to be saved and used
when Azure is selected or defaulted, while marking Google as needing TLS
repair.

**R-086-023**: WHEN provider proxy/runtime paths fail, THE SYSTEM SHALL avoid
logging provider keys, credential-bearing URLs, raw provider response bodies, or
raw stack traces in user-facing output; errors shall flow through the shared
redaction and classification path.

**R-086-024**: WHEN async imagery or metadata downloads run through
`webapp/ts_maps.py`, THE SYSTEM SHALL honor the same configured CA bundle,
TLS-insecure troubleshooting flag, timeout/category mapping, and redacted
URL/error logging as validation, geocoding, and proxy calls.

**R-086-025**: WHEN `scripts/import-tls-ca.ps1` verifies provider TLS, THE
HELPER SHALL print status/category only and SHALL NOT print raw provider
response body snippets.

**R-086-026**: WHEN provider TLS readiness is probed without a real provider
key, THE SYSTEM SHALL treat an expected authenticated provider HTTP response,
including `401`, `403`, or provider-specific invalid-key/request-denied
responses, as `tls_ok` if the verified TLS handshake completed successfully.

**R-086-027**: WHEN the repair helper evaluates certificate candidates, THE
HELPER SHALL use deterministic conservative scoring: reject the leaf
certificate, require `Basic Constraints: CA=true`, prefer `KeyCertSign` when
present, prefer Windows Root stores over intermediate stores, prefer candidates
that appear in the Windows-built provider chain, and stop for manual selection
when multiple equally safe candidates remain.

**R-086-028**: WHEN a Google key fails validation only because Google is in a
repairable TLS state, THE SYSTEM SHALL NOT silently enable Google or persist
the unvalidated Google key in the first implementation. A future
`pending_tls_repair` / `not_enabled` persistence flow may be added only after a
clear support workflow and UI state model are designed.

**R-086-029**: WHEN `/api/config/tls-status` is implemented, THE ENDPOINT SHALL
be read-only, container-scoped, support-safe, and unable to inspect Windows
certificate stores or mutate Docker/Podman trust material.

**R-086-030**: WHEN the Setup Wizard or Settings guides repair, THE UI SHALL
display a copyable support command or support guidance and SHALL NOT launch
host-side certificate import or container-volume repair directly from the
browser app.

**R-086-031**: WHEN support evidence is produced for TLS diagnosis, THE
ARTIFACT SHALL be support-only, gitignored by default, and limited to redacted
provider host, selected engine, GPU mode, result category, and repair result;
it SHALL NOT include raw provider URLs, keys, response bodies, network traces,
raw certificate names, issuer organization, or thumbprints by default. Issuer
organization may be included only behind an explicit support/debug flag.

**R-086-032**: WHEN detection results, session state, export payloads, support
artifacts, or UI-facing tile records include provider request provenance, THE
SYSTEM SHALL avoid exposing credential-bearing provider URLs and SHALL use
redacted URLs, provider/tile metadata, or internal cache/reference identifiers
instead.

## Acceptance Criteria

- [x] A support helper exists as `scripts/repair-provider-tls.ps1` plus
      `scripts/repair-provider-tls.cmd`, and apply-mode mutation delegates to
      `scripts/import-tls-ca.cmd`.
- [x] The helper supports `-Provider google|azure`.
- [x] The helper supports `-Engine auto|docker|podman` or an intentionally
      documented narrower engine set.
- [x] The helper supports `-Gpu off|auto|on` and forwards it to
      `scripts/import-tls-ca.cmd`.
- [x] The helper defaults to dry-run behavior and requires explicit `-Apply`
      or equivalent apply semantics before importing a certificate.
- [x] Dry-run output prints the selected provider host, selected engine, GPU
      mode, candidate certificate summary, and exact repair command.
- [x] Dry-run output is labeled local/support-sensitive when it includes exact
      repair commands, certificate thumbprints, or certificate-selection
      details, and docs warn against pasting it into public issue comments or
      public release evidence.
- [x] Automatic selection never chooses the leaf provider certificate.
- [x] Automatic selection requires CA/trust-anchor evidence and prefers
      Windows Root/CA store-backed certificates.
- [x] If no safe candidate is found, no trust changes are made and the helper
      prints a clear local-IT/support action.
- [x] Manual thumbprint override remains available.
- [x] Manual certificate-file override remains available or is explicitly
      deferred with a documented reason.
- [x] Apply mode reuses the existing import helper rather than duplicating the
      container copy, bundle build, provider verification, and `.env` update.
- [x] Setup Wizard or Settings TLS failure copy points to the new repair helper
      without asking users to share provider keys.
- [x] Package docs for Docker CPU, Docker GPU, Podman CPU, and Podman GPU refer
      to the guided repair helper or explain when the legacy thumbprint command
      is still required.
- [x] A shared provider HTTP/TLS helper exists, for example
      `webapp/ts_provider_http.py`, or the task records a deliberate equivalent
      design.
- [x] `webapp/ts_config.py`, `webapp/ts_geocoding.py`, and Google/Azure map
      proxy handlers use the shared helper or a documented adapter for
      provider HTTP calls.
- [x] `webapp/ts_maps.py` async imagery and metadata downloads use the shared
      helper or a documented `aiohttp` adapter with the configured CA bundle,
      TLS troubleshooting flag, structured category mapping, and redacted URL
      logging.
- [x] Provider HTTP/TLS failures produce stable structured categories for TLS
      untrusted, missing bundle, unusable bundle, timeout, blocked network,
      provider HTTP error, invalid key, and API-not-authorized cases.
- [x] TLS readiness preflight treats expected invalid-key/auth responses as
      `tls_ok` when they prove the container completed a verified TLS
      handshake and received an authentic provider response.
- [x] No-key container-side provider TLS preflight can report Google and Azure
      independently for the selected engine and GPU mode.
- [x] `/api/config/tls-status`, if added, is read-only and container-scoped;
      host-side repair remains in `scripts/repair-provider-tls.cmd`.
- [x] Setup Wizard or Settings preserves structured backend error details and
      renders TLS-specific remediation instead of showing TLS failures as bad
      keys.
- [x] Setup Wizard or Settings can save a valid Azure configuration while
      Google is marked as needing TLS repair, when Azure is the selected/default
      provider.
- [x] A Google key that is blocked by repairable TLS failure is not silently
      enabled, treated as available, or persisted in the first implementation;
      any `pending_tls_repair` / `not_enabled` persistence flow is explicitly
      deferred to future work.
- [x] Certificate candidate selection is deterministic and conservative; if
      multiple equally safe candidates remain, dry run stops and prints manual
      choices rather than auto-importing trust material.
- [x] `scripts/import-tls-ca.ps1` verification output prints status/category
      only and no longer prints raw provider response body snippets.
- [x] Any provider TLS support summary artifact is support-only, gitignored by
      default, redacted, and excludes provider keys, credential-bearing URLs,
      raw response bodies, network traces, raw certificate names, issuer
      organization, and thumbprints by default.
- [x] Detection result payloads, session state, export paths, and support
      artifacts do not expose Google or Azure credential-bearing provider URLs;
      tests cover normal successful detection/tile-result surfaces, not only
      logs and error output.
- [x] Focused tests cover script inclusion, dry-run/apply safety text, GPU-mode
      forwarding, provider selection, and no secret-bearing output strings.
- [x] Focused tests cover provider HTTP/TLS category mapping, Setup Wizard
      structured-error preservation, Azure-save-while-Google-needs-repair
      behavior, map-proxy redaction, `ts_maps.py` async imagery redaction/TLS
      behavior, `import-tls-ca.ps1` body-snippet removal, certificate ambiguity,
      and read-only TLS status behavior.
- [x] Existing provider validation and geocoding TLS tests continue to pass.
- [x] `.agent_work` validation passes.

## Dependencies

- Existing `scripts/import-tls-ca.cmd` and `scripts/import-tls-ca.ps1`.
- Current provider validation behavior in `webapp/ts_config.py`.
- Current TLS helper behavior in `webapp/ts_tls.py`.
- Current provider proxy behavior in `webapp/towerscout.py`.
- Current async map imagery behavior in `webapp/ts_maps.py`.
- Current Setup Wizard behavior in `webapp/js/src/setup-wizard.js`.
- Current Docker/Podman/GPU launch semantics in `scripts/launch.ps1` and
  `scripts/lib/TowerScoutCompose.ps1`.
- Package docs generated under `docs/` and release package inclusion in
  `scripts/package-release.ps1`.
- At least one managed-network validation environment for final live proof.

## Provider Category Mapping

| Source condition | Stable category |
|---|---|
| TLS certificate verification failure from `requests` or `aiohttp` | `tls_ca_untrusted` |
| Configured CA bundle path is missing | `tls_bundle_missing` |
| Configured CA bundle is unreadable, unparseable, or rejected by the HTTP client | `tls_bundle_unusable` |
| DNS, connect, or read timeout | `provider_timeout` |
| DNS failure, connection refused/reset, route unavailable, or managed-network block | `provider_network_blocked` |
| Expected invalid-key/auth response during no-key TLS preflight after successful verified TLS | `tls_ok` |
| Google invalid key, `REQUEST_DENIED`, or equivalent real-key rejection | `invalid_provider_key` |
| Google API disabled, billing disabled, or key lacks required API access | `provider_api_not_authorized` |
| Azure `401`/`403` during real-key validation | `invalid_provider_key` or `provider_api_not_authorized`, based on response detail |
| Non-auth provider `4xx`/`5xx` during runtime calls | `provider_http_error` |

## Implementation Plan

Preferred implementation sequence:

1. Land the shared provider HTTP/TLS categories, CA-bundle handling, and
   redaction contract.
2. Adapt `webapp/ts_maps.py` async imagery/metadata downloads and normal
   detection/session/export URL surfaces to the shared TLS/redaction contract.
3. Preserve structured Setup Wizard and Settings provider statuses, including
   Azure-save behavior when Google needs TLS repair.
4. Add the `repair-provider-tls` dry-run/apply wrapper, selected-engine
   preflight, certificate selection, and import-helper delegation.
5. Update package docs and complete managed-network validation.

Validation package path:

- After implementation and focused local validation, create a clearly labeled
  internal validation package named `tls-validation-2026-06-26` before cutting
  the next official tester-facing package.
- Treat the validation package as a real packaged-path proof, not as a final
  user-facing release: it should exercise the packaged image/digest, scripts,
  docs inclusion, Setup Wizard/Settings behavior, support commands, and
  managed-network TLS repair path.
- Mark any GitHub validation release as draft, prerelease, or otherwise
  internal-validation-only so testers do not confuse it with the next official
  package.
- Use the validation package to reproduce Google TLS failure, run
  `scripts\repair-provider-tls.cmd` dry run, apply repair, restart with the
  same engine/GPU mode, confirm Google reaches normal provider feedback instead
  of TLS CA failure, confirm Azure remains usable, and capture support-safe
  evidence.
- Refine user-facing docs and support wording from validation findings before
  creating the next official tester-facing package.

1. **Shared Provider HTTP/TLS Layer**
   - Add `webapp/ts_provider_http.py` or an equivalent shared module.
   - Centralize TLS verification decisions, configured bundle validation,
     provider labels, timeouts, request execution, structured categories, and
     redacted logging.
   - Migrate `ts_config.py`, `ts_geocoding.py`, and Google/Azure map proxy
     handlers to the shared path.
   - Migrate or adapt `webapp/ts_maps.py` async imagery and metadata download
     helpers to the shared TLS/redaction/category contract. The `aiohttp`
     adapter must use an SSL context that honors configured CA bundles and
     must avoid logging credential-bearing tile or metadata URLs.
   - Replace normal detection/session/export exposure of provider tile URLs
     with redacted URLs, provider/tile metadata, or internal cache/reference
     identifiers so successful workflows do not leak Google `key=` or Azure
     `subscription-key=` values.
   - Preserve existing `TOWERSCOUT_ALLOW_INSECURE_TLS` behavior as a bounded
     troubleshooting path, not a normal product recommendation.

2. **Script Design**
   - Add a new `scripts/repair-provider-tls.ps1` plus
     `scripts/repair-provider-tls.cmd` as the product-facing discovery and
     dry-run wrapper.
   - Keep the actual bundle import in the existing import helper.
   - Define parameters for provider, engine, GPU mode, apply semantics, manual
     thumbprint, manual certificate path, and optional host override for support
     testing.
   - Expose both `-Thumbprint` and `-CertificatePath` on day one, while
     validating that exactly one selection mode is used when manually supplied.
   - Update `scripts/import-tls-ca.ps1` verification so it prints provider
     TLS status/category only, not raw provider response body snippets.

3. **Container Preflight And TLS Chain Discovery**
   - Probe the selected Docker or Podman container path without a provider key
     to classify TLS trust, DNS, timeout, blocked-network, and provider HTTP
     failures before asking users to reason about API keys.
   - Treat expected invalid-key or authorization-style provider responses as
     `tls_ok` during TLS readiness preflight when they prove the container
     completed a verified TLS handshake and received an authentic provider
     response. Real key validity is classified only by real provider-key
     validation.
   - Connect from Windows to the provider host with SNI and no provider key.
   - Capture the chain Windows sees for `maps.googleapis.com` or
     `atlas.microsoft.com`.
   - Exclude the leaf certificate from automatic import.
   - Score candidate certificates deterministically: require Basic Constraints
     `CA=true`, prefer `KeyCertSign` where present, prefer Windows
     `LocalMachine\Root` and `CurrentUser\Root` over intermediate stores,
     prefer candidates present in the Windows-built chain for the provider
     host, and avoid selecting public roots when no local inspection CA is
     detected.
   - If multiple equally safe candidates remain, stay in dry-run/manual mode,
     print the candidate choices, and do not auto-import anything.
   - If container-side preflight shows the provider is blocked rather than
     untrusted, report a network allowlisting/support action instead of a CA
     import recommendation.

4. **Repair Application**
   - Print an exact command in dry-run mode.
   - Label dry-run output as local/support-sensitive when it includes exact
     repair commands, certificate thumbprints, or certificate-selection
     details.
   - In apply mode, invoke `scripts/import-tls-ca.cmd` with the selected
     `-Thumbprint` or `-CertificatePath`, plus `-Engine`, `-Gpu`, and
     `-VerifyProvider`.
   - Print restart guidance using the same engine and GPU mode.

5. **Setup And Docs**
   - Add a read-only, container-scoped `/api/config/tls-status` endpoint if the
     Setup Wizard or Settings need provider TLS status without real provider
     keys. This endpoint must not inspect Windows certificate stores, mutate
     `.env`, import certificates, or alter Docker/Podman volumes.
   - Update Setup Wizard and Settings state handling so invalid keys,
     unauthorized APIs, TLS untrusted, missing/unusable bundles, blocked
     network, timeout, and unknown failures are displayed distinctly.
   - Preserve structured backend categories in frontend validation results
     rather than reducing them to plain error strings.
   - Allow Azure setup to proceed when Azure is valid and selected/defaulted,
     even if Google is marked as needing TLS repair.
   - Do not silently enable Google when its key is blocked by repairable TLS
     failure. For the first implementation, do not persist the unvalidated
     Google key; defer any `pending_tls_repair` / `not_enabled` persistence
     flow until a clear support workflow and UI state model exist.
   - Update TLS failure guidance to reference the new helper.
   - The browser UI should display a copyable support command; host-side repair
     remains in `repair-provider-tls.cmd` / `repair-provider-tls.ps1` and is
     not launched by the browser app.
   - Update Docker/Podman CPU/GPU package docs so support does not need to
     manually hunt for certificate thumbprints first.
   - Make guided repair the primary package-docs path. Keep the existing legacy
     thumbprint and certificate-file commands documented as advanced/support
     fallback for at least one release.
   - If support evidence is generated, write only a redacted support-only
     summary artifact to a gitignored location. Do not include issuer
     organization by default; allow it only behind an explicit support/debug
     flag if later needed.

6. **Tests And Validation**
   - Add backend tests for provider HTTP/TLS category mapping and redaction.
   - Add `aiohttp`/`ts_maps.py` tests for configured CA bundle handling,
     TLS-insecure troubleshooting flag behavior, category mapping, and
     credential-bearing URL redaction.
   - Add frontend tests for structured provider validation state preservation.
   - Add focused script/static tests for parameter forwarding, dry-run default,
     apply gating, package inclusion, no provider-key output patterns, no raw
     provider response body output, and certificate ambiguity behavior.
   - Add tests for read-only `/api/config/tls-status` behavior if the endpoint
     is added.
   - Run focused provider TLS/config tests.
   - Run PowerShell parse checks on the new or modified scripts.
   - Complete one manual managed-network validation pass: reproduce dry run,
     apply repair, restart, and confirm provider validation reaches normal
     provider feedback instead of TLS certificate verification failure.

## Validation Plan

Automated validation should include:

```powershell
python -m pytest tests/unit/test_config.py tests/unit/test_geocoding.py tests/unit/test_flask_routes.py -q -p no:cacheprovider
python .agent_work/scripts/validate_agent_work.py
```

Add or update focused tests for:

- provider HTTP/TLS helper category mapping and redaction
- missing and unusable CA bundle classification
- invalid key versus TLS trust classification
- map proxy/provider runtime calls avoiding credential-bearing logs
- `ts_maps.py` async imagery and metadata downloads honoring configured CA
  bundle behavior, TLS-insecure troubleshooting behavior, category mapping, and
  credential-bearing URL redaction
- Setup Wizard structured-error preservation
- Azure save flow when Google needs TLS repair
- Google key blocked by repairable TLS not being persisted, enabled, or treated
  as available in the first implementation
- read-only `/api/config/tls-status` behavior if the endpoint is added
- normal detection result payloads, session state, export paths, and support
  artifacts not exposing credential-bearing Google or Azure provider URLs
- certificate candidate ambiguity preventing automatic import
- `scripts/import-tls-ca.ps1` verification output omitting raw provider body
  snippets
- script package inclusion, dry-run/apply safety, GPU forwarding, and
  no-secret output patterns

If a new PowerShell script is added, include a parser check such as:

```powershell
powershell -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile('scripts/repair-provider-tls.ps1', [ref]$null, [ref]$null)"
```

Manual validation should include:

- Dry run on a managed network where Google validation currently fails TLS.
- Container-side no-key TLS preflight for Google and Azure on the same managed
  network, confirming expected invalid-key/auth responses count as `tls_ok`.
- Apply mode on the selected engine and GPU mode.
- Restart TowerScout with the same engine and GPU mode.
- Confirm Google validation reaches normal provider feedback instead of
  `CERTIFICATE_VERIFY_FAILED`.
- Confirm Azure validation is not regressed.
- Confirm Azure can be configured as the usable provider while Google remains
  marked as needing TLS repair.
- Confirm a small detection imagery download path does not fail differently
  from validation/geocoding/proxy calls after CA repair.
- Confirm no provider keys or credential-bearing URLs appear in helper output,
  logs, screenshots, evidence summaries, detection result payloads, session
  state, or export/support artifacts.

## Non-Goals

- Do not disable TLS verification as a repair strategy.
- Do not make CA import fully automatic without explicit user/support action.
- Do not build a host-side provider proxy.
- Do not move provider validation out of the container as the main product fix.
- Do not bake organization-specific CA certificates into public release images.
- Do not commit organization-specific certificate names, thumbprints, raw logs,
  screenshots, provider keys, or raw network traces.
- Do not require separate Google browser/server API keys as part of this TLS
  fix; that remains optional hardening for `TASK-076` or a later provider-key
  policy task.
- Do not change cooling-tower detection behavior, map provider feature
  behavior, asset import behavior, or GPU selection semantics.

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Helper selects the wrong certificate | Require CA/basic-constraints evidence, avoid leaf selection, prefer Windows Root/CA store-backed certificates, and keep dry-run default. |
| Helper repairs CPU path while user is on GPU path | Add and forward `-Gpu off|auto|on`; print restart command with the same GPU mode. |
| Certificate diagnostics leak organization details into public evidence | Keep output concise, document support-only handling, and do not place raw diagnostics in public release artifacts. |
| Setup Wizard implies it can repair host trust from inside the container | UI should point to the host-side helper rather than pretending the web app can modify Windows/container trust directly. |
| Applying CA trust broadens container trust too much | Keep explicit apply semantics, prefer least-broad safe CA candidates, and leave manual IT-confirmed thumbprint override. |
| Azure works and Google fails, causing users to suspect key defects | Preserve provider-specific TLS messaging and explain managed-network inspection behavior. |
| Provider validation is fixed but map proxy/geocoding paths still fail differently | Route provider HTTP calls through one shared TLS/error/redaction helper and cover proxy paths with tests. |
| Detection imagery downloads still fail differently after validation is fixed | Include `webapp/ts_maps.py` and its `aiohttp` path in the shared TLS/redaction/category migration. |
| Frontend flattens structured backend failures into generic copy | Preserve backend category/status fields through Setup Wizard and Settings state models. |
| No-key TLS preflight reports expected auth failure as provider failure | Treat invalid-key/auth responses as `tls_ok` only for TLS readiness probes after a verified handshake. |
| Repair helper auto-selects among multiple plausible CAs | Stop in dry-run/manual mode when certificate scoring is ambiguous. |
| Google key is saved as available before TLS repair proves it works | Do not persist or enable Google keys that cannot validate because of repairable TLS in the first implementation; defer any pending-key flow. |
| Browser app crosses host/container trust boundary | Keep `/api/config/tls-status` read-only/container-scoped and run repair only through host-side scripts. |
| Successful detection/session/export payloads leak provider tile URLs with keys | Replace credential-bearing provider URLs with redacted URLs, provider/tile metadata, or internal cache/reference IDs and test normal success paths. |

## Resolved Planning Decisions

1. Add a new `scripts/repair-provider-tls.ps1` plus `.cmd` wrapper. Keep
   `scripts/import-tls-ca.ps1` as the lower-level mutation helper.
2. Expose manual `-CertificatePath` in the new wrapper on day one as a
   support/manual override, with exactly-one selection validation.
3. Use both read-only app diagnosis and host-side scripts when needed:
   `/api/config/tls-status` may report container-side provider TLS readiness,
   while `repair-provider-tls.cmd` performs Windows certificate discovery and
   selected-engine repair.
4. Do not launch host-side repair from the browser app. Setup Wizard and
   Settings should preserve structured status and display copyable guidance.
5. Allow a redacted support-only TLS summary artifact, gitignored by default,
   but keep raw certificate names, thumbprints, keys, URLs, bodies, and network
   traces out of public evidence.
6. Make guided repair the primary package-docs path. Keep manual thumbprint and
   certificate-file commands as advanced/support fallback for at least one
   release.
7. Require managed-network live validation for Google and Azure before the next
   external tester package.
8. Keep separate Google browser/server key policy under `TASK-076`; do not
   block `TASK-086` or the next pilot package on key splitting.
9. Do not include issuer organization in the default TLS support summary
   artifact. Include it only behind an explicit support/debug flag if deeper
   support triage later requires it.
10. Do not persist repair-blocked Google keys in the first implementation.
    Defer any `pending_tls_repair` / `not_enabled` lifecycle until there is a
    clear support workflow and UI state model.

## Remaining Open Questions

None at the current planning-review baseline.

## Implementation Log

### 2026-06-26 - Initial Task Scope Created
**Objective**: Capture the UAT-discovered provider TLS supportability gap and
turn the teammate repair-helper proposal into an actionable TowerScout task.
**Context**: Google Maps validation can fail on managed networks because the
Linux container does not trust the Windows-managed TLS inspection CA. The
existing `import-tls-ca` helper fixes the runtime correctly, but manual
thumbprint discovery is too fragile for tester handoff.
**Decision**: Create a focused task for guided provider TLS diagnosis and
repair. Reuse the existing import helper for actual trust-bundle mutation;
scope new work to discovery, UX, safer certificate selection, Setup
Wizard/bootstrap guidance, docs, and tests.
**Execution**: Added this task document with requirements, acceptance criteria,
implementation plan, validation plan, non-goals, risks, and open questions.
**Validation**: Pending `.agent_work` validator after task registration.
**Next**: Register `TASK-086` in `.agent_work/current-tasks.md`, then implement
only after owner approval to start the task.

### 2026-06-26 - Reviewer Feedback Incorporated
**Objective**: Fold reviewer recommendations into the implementation plan
before starting work.
**Context**: Reviewer agreed that CA import is the correct secure fix, but
identified gaps in provider HTTP centralization, Setup Wizard structured error
handling, no-key container preflight, and Azure-valid/Google-repair behavior.
**Decision**: Expand `TASK-086` rather than creating a separate task because
the helper, backend provider calls, and setup triage all determine whether the
Google TLS issue is fixed from a user's perspective.
**Execution**: Added requirements, acceptance criteria, implementation-plan
steps, validation items, risks, non-goals, and open questions for the shared
provider HTTP/TLS layer, structured categories, container preflight, frontend
state handling, and map-proxy redaction.
**Validation**: Pending `.agent_work` validator.
**Next**: Ask the reviewer to inspect the updated plan before implementation.

### 2026-06-26 - Follow-Up Reviewer Refinements Incorporated
**Objective**: Incorporate the reviewer's Task-086 plan review before approval
for implementation.
**Context**: The reviewer approved the direction but identified remaining gaps
around `ts_maps.py` async imagery downloads, low-level import-helper response
body snippets, no-key preflight success semantics, certificate-candidate
ambiguity, pending Google key persistence, read-only TLS status boundaries, and
estimate accuracy.
**Decision**: Keep `TASK-086` unified rather than splitting it, but raise the
estimate and make the required hardening explicit. Resolve the helper command,
certificate-file override, TLS status endpoint, browser-launch boundary,
support artifact, docs, validation, and `TASK-076` key-splitting questions in
the task file.
**Execution**: Added requirements, acceptance criteria, category mapping,
implementation-plan steps, validation items, risks, resolved planning
decisions, and remaining open questions for the follow-up review findings.
Updated `.agent_work/current-tasks.md` to match the expanded scope and estimate.
**Validation**: Pending `.agent_work` validator.
**Next**: Run `.agent_work` validation and use the updated task as the review
baseline before implementation.

### 2026-06-26 - Updated Reviewer Feedback Incorporated
**Objective**: Incorporate the reviewer's updated Task-086 feedback before
implementation starts.
**Context**: The reviewer approved the expanded TLS repair plan and identified
one remaining gap: normal successful detection/session/export surfaces can
still carry provider URLs with embedded Google or Azure keys. The reviewer also
recommended resolving the two remaining open questions by excluding issuer
organization from default support artifacts and deferring repair-pending Google
key persistence.
**Decision**: Add an explicit normal-flow credential-bearing URL requirement,
accept the safer artifact default, and keep the first implementation from
persisting Google keys that cannot validate because of TLS.
**Execution**: Added `R-086-032`, acceptance criteria, implementation-plan
coverage, validation items, and a risk row for detection/session/export URL
redaction. Updated `R-086-028`, `R-086-031`, resolved planning decisions, and
remaining open questions to reflect the accepted defaults.
**Validation**: Pending `.agent_work` validator.
**Next**: Send the revised task plan back to the reviewer before starting
implementation.

### 2026-06-26 - Final Reviewer Cleanup Incorporated
**Objective**: Align the Task-086 acceptance criteria and implementation
sequence with the reviewer's final cleanup recommendations before
implementation.
**Context**: The reviewer found no remaining blocking design gap, but noted
that the first acceptance criterion still allowed an alternate discovery-mode
implementation even though resolved planning decisions selected a new
`repair-provider-tls` wrapper. The reviewer also called out that dry-run output
can contain support-sensitive repair identifiers and recommended a disciplined
implementation order.
**Decision**: Keep Task-086 as the single implementation task, remove the
alternate helper option from acceptance criteria, explicitly label sensitive
dry-run output, and add a preferred implementation sequence.
**Execution**: Updated the helper acceptance criterion to require
`scripts/repair-provider-tls.ps1` plus `scripts/repair-provider-tls.cmd` with
apply-mode delegation to `scripts/import-tls-ca.cmd`. Added dry-run
local/support-sensitive output criteria and repair-plan guidance. Added a
preferred implementation sequence that starts with shared provider HTTP/TLS and
normal-flow URL redaction before UI triage and script wrapper work.
**Validation**: `python .agent_work/scripts/validate_agent_work.py` passed.
**Next**: Use this plan as the implementation baseline after owner approval.

### 2026-06-26 - Validation Package Path Recorded
**Objective**: Preserve the agreed post-implementation validation-release path
before starting Task-086 implementation.
**Context**: The Google Maps TLS issue requires a managed-network proof before
the next official tester-facing package. The team wants to follow the same
pattern used for GPU validation: publish or stage a clearly labeled validation
package first, then promote the verified flow into the next official
tester-facing package.
**Decision**: Add a validation-package checkpoint to Task-086 rather than
cutting the next official tester-facing package immediately after code
implementation.
**Execution**: Documented the `tls-validation-2026-06-26` package path,
internal-validation-only release labeling, managed-network proof steps,
support-safe evidence expectations, and the rule that user-facing docs are
refined before the next official tester-facing package.
**Validation**: Pending implementation validation.
**Next**: Begin implementation with the shared provider HTTP/TLS layer.

### 2026-06-26 - Initial Implementation Completed
**Objective**: Implement the first Task-086 slice so provider TLS failures are
classified consistently, support-safe, and no longer block a valid default
provider such as Azure Maps.
**Execution**:
- Added `webapp/ts_provider_http.py` as the shared provider HTTP/TLS helper for
  requests, aiohttp SSL contexts, redacted provider URLs, keyless TLS status
  classification, and structured repair categories.
- Updated API-key validation, geocoding, async imagery downloads, map proxy
  routes, and tile/session result payloads to use shared TLS handling and
  redacted provider URLs.
- Added `/api/config/tls-status` for read-only, no-key Google/Azure TLS
  reachability checks.
- Updated setup/settings frontend flows to preserve backend `details`,
  `category`, and `support_action`, and changed settings save behavior so a
  valid selected/default provider can persist even when another provider needs
  TLS repair.
- Added `scripts/repair-provider-tls.ps1` and `.cmd` as a dry-run-first wrapper
  that discovers/ranks Windows CA candidates and delegates apply mode to
  `scripts/import-tls-ca.ps1` / `.cmd`.
- Removed provider response-body snippets from `scripts/import-tls-ca.ps1`
  verification output and added repair scripts to release packaging.
**Validation**:
- `node webapp\build.js` passed and regenerated `webapp/js/towerscout.js`.
- PowerShell parser checks passed for `scripts/repair-provider-tls.ps1` and
  `scripts/import-tls-ca.ps1`.
- `python -m py_compile` passed for changed Python backend modules.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_config.py tests\unit\test_provider_http.py tests\unit\test_flask_routes.py tests\unit\test_geocoding.py tests\unit\test_import_assets_script.py tests\unit\test_error_sanitization.py -q`
  passed: 104 tests.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py::test_package_release_stages_digest_pinned_image -q`
  passed: 1 test.
**Remaining**: Create the internal `tls-validation-2026-06-26` validation
package and run the managed-network proof path before treating this as ready
for the next official tester-facing package.

### 2026-06-26 - Implementation Audit And Documentation Completion
**Objective**: Recheck Task-086 implementation against the acceptance criteria,
correct any source/docs gaps, and record what is complete.
**Findings / Corrections**:
- Corrected `scripts/repair-provider-tls.ps1` dry-run output so it prints the
  guided `scripts\repair-provider-tls.cmd ... -Apply` command. Apply mode now
  invokes the lower-level `scripts\import-tls-ca.cmd` mutation helper directly.
- Added explicit frontend propagation of backend `repair_command` details in
  Setup Wizard and Settings, then rebuilt `webapp/js/towerscout.js`.
- Updated Docker CPU, Docker GPU, Podman CPU, Podman GPU, Quick Start,
  rendered Quick Start HTML, Package Guide, OCI support quick start, runtime
  contract, and `.env.example` so the guided repair helper is the preferred
  path and the low-level import helper is documented as support fallback.
- Added focused coverage for async map download CA-bundle connector usage,
  redacted tile result URLs, frontend structured-error/repair-command
  preservation, certificate ambiguity safety, leaf-certificate exclusion,
  provider/GPU forwarding, and repair-script package inclusion.
- Removed an unused provider HTTP error import from `webapp/towerscout.py`.
**Validation**:
- `node webapp\build.js` passed and regenerated `webapp/js/towerscout.js`.
- PowerShell parser checks passed for `scripts/repair-provider-tls.ps1` and
  `scripts/import-tls-ca.ps1`.
- `python -m py_compile webapp\ts_provider_http.py webapp\ts_config.py webapp\ts_geocoding.py webapp\ts_maps.py webapp\towerscout.py`
  passed.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_config.py tests\unit\test_provider_http.py tests\unit\test_frontend_provider_tls.py tests\unit\test_flask_routes.py tests\unit\test_geocoding.py tests\unit\test_import_assets_script.py tests\unit\test_task_080_uat_followups.py tests\unit\test_release_package_script.py::test_package_release_stages_digest_pinned_image -q`
  passed: 110 tests.
- `git diff --check` passed.
- `python .agent_work\scripts\validate_agent_work.py` passed.
**Remaining**: Build the internal `tls-validation-2026-06-26` validation
package and prove the dry-run/apply/restart path on a managed network before
promoting the verified flow into the next official tester-facing package.

### 2026-06-26 - Internal TLS Validation Package Staged
**Objective**: Create a traceable internal validation package named
`tls-validation-2026-06-26` without rc naming.
**Context**: The validation package needs to prove the Task-086 source changes
through the packaged path before the next official tester-facing package. The
backend/frontend TLS behavior lives inside the container image, so the package
must pin a newly published image built from the Task-086 source ref.
**Execution**:
- Created branch `feature/task-086-provider-tls-repair`.
- Committed Task-086 source/docs/tests as
  `1566163a86c92f59763014e6ad317067721f91c0`.
- Pushed the branch to `origin`.
- Published CPU validation image with GitHub Actions run
  `https://github.com/J-Schulein/TowerScout/actions/runs/28258939025`.
- Created and pushed annotated git tag `tls-validation-2026-06-26`.
- Generated local package folder
  `dist\tls-validation-2026-06-26`.
- Created the GitHub validation prerelease with tag
  `tls-validation-2026-06-26` at
  `https://github.com/J-Schulein/TowerScout/releases/tag/tls-validation-2026-06-26`.
**Output**:
- Image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-cpu@sha256:e2cf5de79338b57e5c2094f3b633d857e130a9688daccc93611b1bc3ce4df105`.
- Control ZIP:
  `towerscout-tls-validation-2026-06-26.zip`.
- Control ZIP SHA-256:
  `fced0b089753556b2b36ca75d3fafc12dc3fe03cbad2948f1c8810c1d0585ce5`.
- Asset ZIP:
  `towerscout-tls-validation-2026-06-26-assets-towerscout-v1-assets-2026-05-05.zip`.
- Asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**:
- Container publish workflow completed successfully.
- `summarize_release_package.py` reported the expected package shape.
- `check_release_manifest.py` passed for the staged package manifest.
- Control ZIP and asset ZIP checksum sidecars matched `Get-FileHash`.
- Staged package `SHA256SUMS.txt` verification passed.
- Package includes `scripts\repair-provider-tls.*`, `scripts\import-tls-ca.*`,
  runtime-specific Docker/Podman CPU/GPU guides, and pinned `IMAGE.txt`.
**Caveat**: Package generation used `-AllowDirtySource` because an unrelated
local untracked `.agent_work/context/guides/TowerScout-RC-Package-Cleanup-Guide.docx`
artifact exists outside the Task-086 source commit. This package is explicitly
internal-validation-only and not an official release artifact.
**Next**: Run the managed-network validation proof: download/extract the
validation assets, reproduce Google TLS failure, run
`scripts\repair-provider-tls.cmd` dry run, apply with support approval, restart
with the same engine/GPU mode, confirm Google reaches normal provider feedback
instead of `CERTIFICATE_VERIFY_FAILED`, and confirm Azure remains usable.

### 2026-06-26 - Validation Release Asset Visibility Fixed
**Objective**: Ensure the GitHub `tls-validation-2026-06-26` page exposes the
actual TowerScout package assets instead of only GitHub source archives.
**Context**: The initial GitHub release was left as a draft and therefore the
visible tag page showed only automatic source archives. The package assets had
uploaded to the draft release but were not visible on the public prerelease
page.
**Execution**: Published the existing release as a prerelease with
`gh release edit tls-validation-2026-06-26 --draft=false --prerelease`.
**Validation**: `gh release view tls-validation-2026-06-26` now reports
`draft: false`, `prerelease: true`, URL
`https://github.com/J-Schulein/TowerScout/releases/tag/tls-validation-2026-06-26`,
and all four initial assets:
- `towerscout-tls-validation-2026-06-26.zip`
- `towerscout-tls-validation-2026-06-26.zip.sha256`
- `towerscout-tls-validation-2026-06-26-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-tls-validation-2026-06-26-assets-towerscout-v1-assets-2026-05-05.zip.sha256`
**Next**: Correct the package shape to publish CPU and CUDA app ZIP variants
before managed-network proof.

### 2026-06-26 - CPU/CUDA Validation Package Split Corrected
**Objective**: Replace the initial unsuffixed validation Application Package
ZIP with explicit CPU and CUDA 12.1 package variants so the TLS repair path can
be validated through both normal CPU and support-assigned GPU package flows.
**Context**: The initial `tls-validation-2026-06-26` release exposed a single
unsuffixed Application Package ZIP. That was not the package shape established
for the current release path, where CPU users and GPU validation use separate
digest-pinned app ZIPs and one shared Model & Data Package ZIP.
**Decision**: Treat the unsuffixed ZIP as superseded validation output. Keep
the validation tag and prerelease name unchanged, publish
`-cpu` and `-cuda121` app ZIPs, and keep the shared asset ZIP unsuffixed.
Rebuild the CUDA image from the validation tag so both CPU and CUDA image
metadata point to source ref `1566163a86c92f59763014e6ad317067721f91c0`.
**Execution**:
- Confirmed the earlier CPU image was built from tag source ref
  `1566163a86c92f59763014e6ad317067721f91c0`.
- Published the CUDA 12.1 validation image from tag
  `tls-validation-2026-06-26` with GitHub Actions run
  `https://github.com/J-Schulein/TowerScout/actions/runs/28261884499`.
- Generated package variants from the validation source ref:
  `towerscout-tls-validation-2026-06-26-cpu.zip` and
  `towerscout-tls-validation-2026-06-26-cuda121.zip`.
- Removed the old local unsuffixed Application Package folder, ZIP, and
  checksum sidecar from `dist\tls-validation-2026-06-26`.
- Uploaded the CPU/CUDA package ZIPs and checksum sidecars to the GitHub
  prerelease.
- Deleted the obsolete unsuffixed Application Package ZIP and checksum sidecar
  from the GitHub prerelease.
- Updated the validation prerelease notes to describe the CPU and CUDA package
  choices and to avoid any rc7 implication.
**Output**:
- CPU image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-cpu@sha256:e2cf5de79338b57e5c2094f3b633d857e130a9688daccc93611b1bc3ce4df105`.
- CUDA 12.1 image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-cuda121@sha256:aa7645299010c1eb600b1c40b1c9841521b0970f08c2384d930861dec3ea66c4`.
- CPU Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-cpu.zip`.
- CPU Application Package ZIP SHA-256:
  `c56a7f87db19f7d1d78c3e708b189036d799ae3dfced3701735c2487fa7affd4`.
- CUDA Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-cuda121.zip`.
- CUDA Application Package ZIP SHA-256:
  `cf41a5193b6dceee6414b5a3e3050772080c03d34d2fdd1a343d1ce345ce9dc0`.
- Shared Model & Data Package ZIP:
  `towerscout-tls-validation-2026-06-26-assets-towerscout-v1-assets-2026-05-05.zip`.
- Shared Model & Data Package ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**:
- CUDA tag-based container publish completed successfully with source ref
  `1566163a86c92f59763014e6ad317067721f91c0`.
- `summarize_release_package.py` passed for both CPU and CUDA package ZIPs.
- `check_release_manifest.py` passed for both generated package manifests.
- `IMAGE.txt`, `.env.example`, and `release-manifest.v1.json` in each package
  identify the correct package flavor and pinned image digest.
- Both package manifests identify the same shared asset bundle filename and
  SHA-256.
- Control ZIP and asset ZIP checksum sidecars matched `Get-FileHash`.
- Package `SHA256SUMS.txt` verification passed for both CPU and CUDA staging
  folders.
- `gh release view tls-validation-2026-06-26` reports `draft: false`,
  `prerelease: true`, target commit
  `1566163a86c92f59763014e6ad317067721f91c0`, and the six expected assets:
  CPU ZIP/checksum, CUDA ZIP/checksum, and shared asset ZIP/checksum.
**Caveat**: Package generation still used `-AllowDirtySource` because the
unrelated untracked
`.agent_work/context/guides/TowerScout-RC-Package-Cleanup-Guide.docx` artifact
exists locally. The package was generated from the validation source ref, and
the artifact remains ignored/unpublished.
**Next**: Continue with managed-network proof using the corrected validation
prerelease assets.

### 2026-06-26 - Managed-Network Validation Failure Root-Cause Fix
**Objective**: Triage the downloaded CPU validation package failure and correct
the source before producing the next validation package.
**Context**: Managed-network testing of the downloaded
`tls-validation-2026-06-26-cpu` package reproduced the Google provider TLS
failure after running the documented manual repair command with the previously
identified thumbprint. The helper copied CA material into the container, but
provider TLS verification still failed, so `.env` remained pointed at the
stock Linux trust bundle and the restart could not use the repaired bundle.
**Decision**: Treat the first validation package as superseded for TLS proof.
Fix the discovery helper instead of asking testers to manually hunt for a
different thumbprint.
**Execution**:
- Confirmed the pasted support output contained no raw provider API key.
- Confirmed the package `.env` still used the default Linux CA bundle after
  the failed repair because the helper exits before persisting
  `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` when verification fails.
- Probed the running validation container without API keys and confirmed the
  combined CA bundle existed, but no-key Google TLS still failed with a
  certificate-verification category.
- Identified the implementation bug: `scripts/repair-provider-tls.ps1`
  rebuilt a new Windows chain from the leaf certificate after the TLS
  handshake, which can collapse to only the provider leaf on managed networks.
  It did not preserve the chain supplied to the TLS validation callback, which
  contained the real organization Root/CA chain needed for conservative
  candidate selection.
- Updated `scripts/repair-provider-tls.ps1` to capture callback chain elements,
  clone their certificate raw data, include issuer details in the local
  support-sensitive dry-run output, and continue falling back to leaf-chain
  reconstruction only if the callback provides no chain.
- Updated `scripts/import-tls-ca.ps1` verification so Google/Azure no-key TLS
  checks report concise status/category lines, accept expected provider HTTP
  feedback as TLS success, catch certificate and request exceptions without a
  Python traceback, and state that `.env` was not updated when verification
  fails.
- Added focused static regression assertions in
  `tests/unit/test_import_assets_script.py`.
**Validation**:
- PowerShell parser checks passed for `scripts/repair-provider-tls.ps1` and
  `scripts/import-tls-ca.ps1`.
- `.venv\Scripts\python.exe -m pytest tests/unit/test_import_assets_script.py
  -q -p no:cacheprovider` passed: 4 tests.
- Live dry run of `scripts\repair-provider-tls.cmd -Provider google -Engine
  docker -Gpu off` now captures the full managed-network callback chain and
  selects the store-backed organization Root CA candidate instead of stopping
  at the provider leaf. Raw certificate identities and thumbprints are treated
  as local support-sensitive output and are not recorded here.
**Next**: Commit the source fix, rebuild/publish replacement internal CPU and
CUDA validation images/packages, then re-run the managed-network repair proof
from a downloaded package before planning the official rc7 package.

### 2026-06-26 - V2 TLS Validation Package Published
**Objective**: Rebuild and publish replacement internal validation packages
from the post-fix Task-086 source ref.
**Context**: The first `tls-validation-2026-06-26` validation release was
superseded for TLS proof because dry-run chain discovery could miss the actual
organization Root/CA chain. The replacement package needed a new validation tag
without rc naming so testers do not confuse it with the future rc7 package.
**Decision**: Use `tls-validation-2026-06-26-V2` as a separate validation tag
and prerelease. Keep CPU and CUDA 12.1 Application Package ZIPs separate and
use one shared V2-named Model & Data Package ZIP.
**Execution**:
- Created and pushed annotated git tag `tls-validation-2026-06-26-V2`.
- Published CPU and CUDA 12.1 validation images from source ref
  `280b073a40d0d95098de9fe443b25fddab6a90a7`.
- Generated digest-pinned package variants under
  `dist\tls-validation-2026-06-26-V2`.
- Reused the already-validated asset ZIP bytes with a V2 asset filename and
  checksum sidecar.
- Created the GitHub prerelease at
  `https://github.com/J-Schulein/TowerScout/releases/tag/tls-validation-2026-06-26-V2`.
**Output**:
- CPU image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-V2-cpu@sha256:756aae17137d98e1a970814f43497b1da815c110bf850880e5483a7faa5fb7a7`.
- CUDA 12.1 image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-V2-cuda121@sha256:794a501899d5edecc023a8f88dfcb60ce961ca02b61a57e3455d18fadb92d436`.
- CPU Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-V2-cpu.zip`.
- CPU Application Package ZIP SHA-256:
  `dc739ffb9f0f1f4a0151706398afed5210bbe6e2c1cc797e45c0418a2951bf67`.
- CUDA Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-V2-cuda121.zip`.
- CUDA Application Package ZIP SHA-256:
  `183907830ee425a49033debf5c30c7a30c13fbc4ddfbea70693d43c0b72b54c8`.
- Shared Model & Data Package ZIP:
  `towerscout-tls-validation-2026-06-26-V2-assets-towerscout-v1-assets-2026-05-05.zip`.
- Shared Model & Data Package ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**:
- GitHub Actions CPU publish run `28266443448` passed.
- GitHub Actions CUDA 12.1 publish run `28266444732` passed.
- `summarize_release_package.py` passed for both CPU and CUDA package ZIPs.
- `check_release_manifest.py` passed for both generated package manifests.
- Control ZIP and asset ZIP checksum sidecars matched `Get-FileHash`.
- Package `SHA256SUMS.txt` verification passed for both CPU and CUDA staging
  folders.
- Package manifests identify source ref
  `280b073a40d0d95098de9fe443b25fddab6a90a7`, the expected image digests, and
  the same shared V2 asset ZIP name/hash.
- Generated package folders do not include local `.env`, logs, temp/session
  files, uploads, cache, screenshots, or raw support artifacts.
- `gh release view tls-validation-2026-06-26-V2` reports `draft: false`,
  `prerelease: true`, target commit
  `280b073a40d0d95098de9fe443b25fddab6a90a7`, and the six expected assets:
  CPU ZIP/checksum, CUDA ZIP/checksum, and shared asset ZIP/checksum.
**Caveat**: Package generation used `-AllowDirtySource` because an unrelated
local untracked cleanup guide artifact exists outside the Task-086 source
commit. This package is explicitly internal-validation-only and not an official
release artifact.
**Next**: Download/extract the V2 validation assets, reproduce the managed
Google TLS failure, run dry-run/apply/restart through the package, and confirm
Google reaches normal provider feedback instead of `CERTIFICATE_VERIFY_FAILED`.

### 2026-06-26 - V2 Managed-Network Proof And Verifier Gap
**Objective**: Interpret the downloaded V2 CPU package validation results and
identify whether the remaining failure is in the CA repair concept or in the
packaged helper implementation.
**Context**: Managed-network V2 validation showed the dry-run candidate
selection fix worked: the helper selected the expected store-backed
organization/root CA candidate. The normal apply path then failed before
persisting `.env` because the container-side provider verifier received a
malformed Python command. A follow-up support command imported the same CA
material with `-VerifyProvider none`, restarted TowerScout, and Google key
validation completed.
**Decision**: Treat V2 as a useful proof of the underlying CA bundle approach,
but not as the final proof for the documented user-facing repair command. Build
V3 specifically to remove the inline verifier command fragility while keeping
the same CA import, `.env` persistence, and restart behavior.
**Execution**:
- Reviewed redacted V2 terminal output from the downloaded CPU package.
- Confirmed the manual bypass path updated `.env` to:
  `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem` and
  `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- Confirmed the restarted app reached `state: ready`, Google was configured,
  and logs no longer showed `CERTIFICATE_VERIFY_FAILED`.
- Confirmed the raw output includes local certificate identity/thumbprint
  details and should remain support-sensitive rather than public evidence.
**Validation**:
- V2 workaround proof demonstrated the container trust-store repair and
  persistent CA bundle path are correct for the managed-network Google setup
  failure.
- V2 did not prove the normal `repair-provider-tls.cmd ... -Apply` command
  because the operator had to use `import-tls-ca.cmd ... -VerifyProvider none`
  to bypass the broken inline verifier.
**Next**: Patch `scripts/import-tls-ca.ps1` so provider verification runs from
a temporary script file inside the container, then build and publish V3 CPU and
CUDA validation packages.

### 2026-06-26 - V3 Provider Verifier Source Fix
**Objective**: Fix the V2 provider-verification command construction issue so
the normal documented repair command can verify Google/Azure TLS without
requiring `-VerifyProvider none`.
**Context**: V2 used `docker compose exec ... python -c <multiline script>` for
the no-key provider TLS probe. The downloaded-package validation showed Compose
argument handling could strip Python string quotes, producing a syntax error
instead of a provider TLS status/category result. The CA bundle itself worked
once verification was bypassed.
**Decision**: Keep the same no-key Google/Azure TLS probe logic, but write the
probe to a temporary local `.py` file, copy it into the running TowerScout
container, execute `python /tmp/towerscout-tls-verify-*.py` with
`REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` pointed at the combined bundle, then
remove the temporary container file while preserving the verifier exit code.
**Execution**:
- Updated `scripts/import-tls-ca.ps1` to rename the generic copy helper to
  `Copy-TowerScoutFileIntoContainer` and reuse it for both CA material and the
  temporary provider verifier script.
- Added `Invoke-TowerScoutTlsProviderVerification` to create/copy/run/cleanup
  the verifier script without inline `python -c` quoting.
- Kept `-VerifyProvider none` as a support escape hatch, but the default
  `google`/`azure` verifier now runs through a file path.
- Added a focused regression assertion in
  `tests/unit/test_import_assets_script.py` proving the importer no longer
  invokes Python as `python -c` for provider verification.
**Validation**:
- PowerShell parser checks passed for `scripts/import-tls-ca.ps1` and
  `scripts/repair-provider-tls.ps1`.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_import_assets_script.py
  -q -p no:cacheprovider` passed: 4 tests.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_import_assets_script.py
  tests\unit\test_release_package_script.py tests\unit\test_config.py
  tests\unit\test_flask_routes.py -q -p no:cacheprovider` passed: 80 tests.
- `python .agent_work\scripts\validate_agent_work.py` passed.
**Next**: Commit and push the V3 source fix, create tag
`tls-validation-2026-06-26-V3`, publish CPU/CUDA images from that tag, rebuild
digest-pinned CPU/CUDA validation packages, publish the V3 prerelease assets,
and repeat downloaded-package managed-network validation through the normal
`repair-provider-tls.cmd ... -Apply` path.

### 2026-06-26 - V3 TLS Validation Package Published
**Objective**: Build and publish the V3 internal validation package set from
the committed provider-verifier source fix.
**Context**: V2 proved the CA bundle import and `.env` persistence strategy
when provider verification was bypassed, but did not prove the normal
`repair-provider-tls.cmd ... -Apply` path because the inline Python verifier
could be malformed by Compose argument handling. V3 needed fresh CPU and CUDA
12.1 images/packages from the source fix.
**Decision**: Use `tls-validation-2026-06-26-V3` as a separate internal
validation tag and prerelease. Keep separate CPU and CUDA 12.1 Application
Package ZIPs, with one shared V3-named Model & Data Package ZIP using the
already-validated asset bytes.
**Execution**:
- Committed the source fix as
  `cd362ec976a37c1f5fd13bac03c8e657720f49ba`.
- Pushed branch `feature/task-086-provider-tls-repair`.
- Created and pushed annotated git tag `tls-validation-2026-06-26-V3`.
- Published CPU and CUDA 12.1 validation images from source ref
  `cd362ec976a37c1f5fd13bac03c8e657720f49ba`.
- Generated digest-pinned package variants under
  `dist\tls-validation-2026-06-26-V3`.
- Reused the already-validated asset ZIP bytes with a V3 asset filename and
  checksum sidecar.
- Created the GitHub prerelease at
  `https://github.com/J-Schulein/TowerScout/releases/tag/tls-validation-2026-06-26-V3`.
**Output**:
- CPU publish run: `28268701301`.
- CUDA 12.1 publish run: `28268704018`.
- CPU image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-V3-cpu@sha256:630ef39c12441cb1ed27330338a95f628a47b7982eb441b245c6b3fe194e16ad`.
- CUDA 12.1 image:
  `ghcr.io/j-schulein/towerscout:tls-validation-2026-06-26-V3-cuda121@sha256:b76a1733869e04d38489031490c657ccfda47284b1e9c5ac56b1c5e9725d3c37`.
- CPU Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-V3-cpu.zip`.
- CPU Application Package ZIP SHA-256:
  `172f9fe27a96aa0c3adbb8b3e1c9a71b1294df9f96624b74cecd0c2af672527d`.
- CUDA Application Package ZIP:
  `towerscout-tls-validation-2026-06-26-V3-cuda121.zip`.
- CUDA Application Package ZIP SHA-256:
  `356e73c112eba077ba01feaea1a1bda8fddad0f1172a22a956ab36de9e202308`.
- Shared Model & Data Package ZIP:
  `towerscout-tls-validation-2026-06-26-V3-assets-towerscout-v1-assets-2026-05-05.zip`.
- Shared Model & Data Package ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**:
- GitHub Actions CPU publish run `28268701301` passed.
- GitHub Actions CUDA 12.1 publish run `28268704018` passed.
- Remote annotated tag `tls-validation-2026-06-26-V3` dereferences to
  `cd362ec976a37c1f5fd13bac03c8e657720f49ba`.
- `summarize_release_package.py` passed for both CPU and CUDA package ZIPs.
- `check_release_manifest.py` passed for both generated package manifests.
- Control ZIP and asset ZIP checksum sidecars matched `Get-FileHash`.
- Package `SHA256SUMS.txt` verification passed for both CPU and CUDA staging
  folders.
- Package manifests identify source ref
  `cd362ec976a37c1f5fd13bac03c8e657720f49ba`, the expected image digests, and
  the same shared V3 asset ZIP name/hash.
- Generated package folders do not include local `.env`, logs, temp/session
  files, uploads, cache, screenshots, or raw support artifacts.
- `gh release view tls-validation-2026-06-26-V3` reports `draft: false`,
  `prerelease: true`, and the six expected assets: CPU ZIP/checksum, CUDA
  ZIP/checksum, and shared asset ZIP/checksum.
**Caveat**: Package generation used `-AllowDirtySource` because an unrelated
local untracked cleanup guide artifact exists outside the Task-086 source
commit. This package is explicitly internal-validation-only and not an official
release artifact. GitHub's release API reports `targetCommitish: main` for the
release object, but the published annotated tag itself dereferences to the
expected V3 source commit and the package manifests embed that source ref.
**Next**: Download/extract the V3 validation assets, run the normal
`scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off
-Apply` path on the managed network, restart TowerScout, and confirm Google
key validation succeeds without `CERTIFICATE_VERIFY_FAILED` and without using
`-VerifyProvider none`.

### 2026-06-26 - V3 CPU Managed-Network Proof Passed
**Objective**: Validate the V3 CPU package through the downloaded-package,
managed-network Google TLS repair path using the normal support-facing command.
**Context**: V3 was created to prove the normal
`scripts\repair-provider-tls.cmd ... -Apply` flow after replacing V2's inline
`python -c` verifier with a temporary in-container verifier script. The tester
ran the V3 CPU package from a downloaded release asset and accidentally ran
`status`/`logs` before the final local `.env` `Select-String`, which does not
invalidate the result because the stop/start happened before those checks.
**Decision**: Treat this as a V3 CPU managed-network proof pass with one
evidence caveat: the pasted transcript does not include the explicit
`google_tls_status=...` verifier line or the import helper's final
`Updated .env...` line, but it does show the V3 verifier-script copy path, no
`-VerifyProvider none`, persisted CA bundle settings, no V2 syntax failure, no
TLS certificate failure, and successful Google setup after restart.
**Execution**:
- Ran `setup-towerscout.cmd -Engine docker` from the downloaded V3 CPU package.
- Confirmed the V3 CPU image digest in the package/runtime:
  `sha256:630ef39c12441cb1ed27330338a95f628a47b7982eb441b245c6b3fe194e16ad`.
- Ran the normal repair command:
  `scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply`.
- Confirmed the wrapper selected a store-backed organization/root CA candidate
  and delegated to `scripts\import-tls-ca.cmd -Engine docker -Gpu off
  -VerifyProvider google -Thumbprint <redacted>`.
- Confirmed the V3 helper copied the temporary verifier script to
  `/tmp/towerscout-tls-verify-*.py`, proving the package used the V3 script-file
  verifier path rather than the V2 inline `python -c` path.
- Restarted with `scripts\stop.cmd -Engine docker` and
  `start.bat -Engine docker -Gpu off`.
- Confirmed `.env` persisted:
  `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem` and
  `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- Confirmed readiness reached `state: ready`, Google was configured, and the
  frontend Google key endpoint reported a key available.
**Validation**:
- No API key pattern was present in the pasted output.
- No `-VerifyProvider none` bypass was used.
- No `SyntaxError`, traceback, or `CERTIFICATE_VERIFY_FAILED` appeared.
- Asset status remained `ok`, runtime selected CPU as expected, and package
  image digest matched the V3 CPU release digest.
- Raw certificate subjects/thumbprints remain support-sensitive and are not
  recorded in this task evidence.
**Next**: Record owner-confirmed CUDA managed-network validation and close
Task-086 as the rc7 TLS repair baseline.

### 2026-06-29 - CUDA Managed-Network Confirmation And Completion
**Objective**: Close Task-086 after confirming that the V3 TLS repair fix works
for both CPU and CUDA validation package paths on a managed TLS-inspected
network.
**Context**: The downloaded V3 CPU package already passed the normal
`repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply` path
without `-VerifyProvider none`. The remaining decision was whether to run the
CUDA 12.1 V3 package through the same managed-network proof or accept CPU live
proof plus CUDA package/image validation.
**Decision**: Treat Task-086 as complete based on owner-reported confirmation
that the Task-086 fix also works with CUDA on a managed network. Keep the
manual/guided command path from Task-086 as the rc7 baseline. Keep
`TASK-087` as a separate follow-on plan for a one-click host-side repair helper
after rc7 unless tester evidence promotes it.
**Execution**:
- Recorded owner confirmation that the V3 CUDA package path works on a managed
  network with the Task-086 TLS repair fix.
- Kept the evidence support-safe by not recording raw terminal output,
  certificate subjects, certificate thumbprints, provider keys, provider
  responses, or local environment details.
- Updated Task-086 status to completed.
**Validation**:
- V3 CPU downloaded-package managed-network proof passed the normal repair path
  without `-VerifyProvider none`.
- V3 CPU and CUDA 12.1 image publish and package validation previously passed.
- V3 CUDA managed-network behavior is owner-confirmed as working for the
  Task-086 fix.
**Next**: Use Task-086 as the rc7 provider TLS repair baseline, then proceed
with Sprint 6 closeout planning, repository housekeeping, rc7 package/docs
refinement, and rc7 publication sequencing.

### 2026-06-29 - RC7 Setup Wizard Repair Command Check
**Objective**: Confirm the startup wizard's TLS/CA repair guidance before
building rc7 packages.
**Finding**: The wizard already consumed the backend `repair_command` value, but
the backend helper defaulted that command to `-Engine auto -Gpu off`. That was
acceptable for the default Docker CPU path, but it was not precise enough for
CUDA or Podman users because support guidance should preserve the engine and GPU
mode selected at setup.
**Correction**:
- Updated the provider repair command helper to resolve
  `TOWERSCOUT_CONTAINER_ENGINE` and `TOWERSCOUT_GPU_MODE` from the running
  container, with allowlisted fallbacks to `auto` and `off` when runtime metadata
  is missing or invalid.
- Kept the wizard command as the support-reviewed dry run rather than adding
  `-Apply`; the dry run remains the intended first step because it prints the
  safe apply command after CA candidate selection.
- Added unit coverage for runtime-specific command generation, invalid runtime
  fallback handling, and the exact validation payload command that the startup
  wizard displays.
**Validation**:
- `.venv\Scripts\python.exe -m pytest tests/unit/test_provider_http.py
  tests/unit/test_config.py tests/unit/test_flask_routes.py
  tests/unit/test_frontend_provider_tls.py -q -p no:cacheprovider --tb=short`
  passed with 80 tests.
- `.venv\Scripts\python.exe -m py_compile webapp\ts_provider_http.py
  webapp\ts_config.py` passed.
- Command-generation probe confirmed:
  `docker/off`, `docker/on`, `podman/off`, and `podman/on` produce matching
  `.\scripts\repair-provider-tls.cmd -Provider google -Engine <engine> -Gpu
  <mode>` commands.
**Decision**: Treat the startup wizard TLS/CA command guidance as corrected for
rc7 packaging once this change is included in the release source ref.
