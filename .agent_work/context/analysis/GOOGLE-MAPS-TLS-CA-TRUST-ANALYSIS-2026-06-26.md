# Google Maps TLS CA Trust Analysis

**Date**: 2026-06-26
**Scope**: TowerScout container provider validation, Google Maps TLS failures on managed networks, and mitigation options
**Status**: Analysis and recommendation

## Executive Summary

The Google Maps key validation failure is a container trust-store problem, not
evidence that the Google key is bad by default.

TowerScout runs provider validation and several provider API calls from inside a
Linux container. The container has its own Debian/Python certificate trust
bundle. It does not automatically inherit the Windows enterprise certificate
store. On managed networks that inspect HTTPS traffic, the network security
tool presents a locally issued certificate chain for provider traffic. Windows
and the host browser trust that chain because the organization root or
intermediate CA is installed on the workstation. The container does not trust it
until TowerScout imports that CA material into the container-visible CA bundle.

This explains the observed behavior:

1. Google Maps validation can fail with `CERTIFICATE_VERIFY_FAILED` even when
   the key is correct.
2. Importing the managed-network TLS inspection CA into the selected
   Docker/Podman config volume fixes the failure while preserving normal TLS
   verification.
3. Azure Maps can pass on the same workstation because the local network may
   treat `atlas.microsoft.com` differently from `maps.googleapis.com`, or
   because the Azure validation route is not being intercepted in the same way.

Recommended path:

1. Keep the current CA import design as the secure baseline.
2. Add a guided diagnosis/import experience so support or the user does not
   need to manually identify certificate thumbprints.
3. Avoid using insecure TLS bypass as a product solution.
4. Treat host-side or browser-side validation as diagnostic only unless the
   entire Google provider call path is moved out of the container, which is a
   larger architecture change with key-handling and support risks.

## Current TowerScout Behavior

TowerScout uses both browser-side map SDKs and server-side provider API calls.
The TLS problem appears on the server-side calls made from the container.

Relevant code and package behavior:

- `webapp/ts_config.py` validates provider keys with Python `requests`.
  Google validation calls both `https://maps.googleapis.com/maps/api/staticmap`
  and `https://maps.googleapis.com/maps/api/geocode/json`.
- `webapp/ts_geocoding.py` performs server-side geocoding and reverse
  geocoding with Python `requests`.
- `webapp/ts_tls.py` centralizes TLS behavior. TLS verification is enabled by
  default. `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` are treated as configured
  CA bundle paths. `TOWERSCOUT_ALLOW_INSECURE_TLS=1` is an explicit local
  fallback, not normal release posture.
- `compose.yaml` sets default CA paths to the Debian bundle:
  `/etc/ssl/certs/ca-certificates.crt`.
- `scripts/import-tls-ca.ps1` can export a Windows certificate by thumbprint,
  include the Windows chain, copy it into the container config volume, append it
  to the Debian CA bundle, and set both `REQUESTS_CA_BUNDLE` and
  `SSL_CERT_FILE` to `/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- Docker and Podman have separate named volumes, so the CA import must be run
  for the selected engine.

The current helper is intentionally conservative: it does not disable TLS. It
adds the organization's trusted inspection CA to the bundle used by container
processes, then verifies the provider endpoint with an invalid test key. A good
TLS repair should return a normal provider response, such as an invalid-key
response, rather than a certificate verification failure.

## What Is Actually Failing

The failure is in certificate chain validation.

For a normal direct Google request, the container receives a certificate chain
issued by a public CA already present in the Debian/Python trust bundle. TLS
verification succeeds.

On a managed network with HTTPS inspection, the flow is different:

1. The container connects to `maps.googleapis.com`.
2. A proxy or endpoint security product intercepts the HTTPS session.
3. That product presents a replacement certificate for the Google hostname,
   signed by the organization's local inspection CA.
4. Windows trusts that local CA because enterprise policy installed it in the
   Windows certificate store.
5. The Linux container does not trust the local CA because it has its own CA
   bundle.
6. Python `requests` rejects the chain and raises an SSL certificate
   verification error.

The important point is that both sides can be behaving correctly. The proxy is
following the organization's managed-network policy, and Python is correctly
refusing a chain that its trust store does not recognize.

## Why The Browser May Work While TowerScout Validation Fails

The host browser and the container are different trust environments.

The browser runs on Windows and uses the Windows-managed trust store. If the
organization pushed its inspection CA to the workstation, the browser can load
Google or Azure pages without warning.

TowerScout's provider validation runs inside the container. The container uses a
Linux CA bundle and Python `requests`/`certifi` behavior. It does not
automatically know about Windows enterprise roots or intermediates.

This is why "Google works in the browser" does not prove that "Google provider
validation must work from the container."

## Why Azure Maps Can Work While Google Maps Fails

This is most likely network policy, endpoint routing, or validation-path
asymmetry, not a fundamental Google-versus-Azure TLS quality difference.

Likely explanations:

1. **Different inspection policy by domain**: The managed network may inspect
   `maps.googleapis.com` but pass `atlas.microsoft.com` through directly.
2. **Different inspection chain**: Azure traffic may be intercepted by a chain
   that the container already trusts, while Google traffic is intercepted by an
   enterprise CA that only Windows trusts.
3. **Different allowlist behavior**: Microsoft/Azure endpoints are commonly
   allowlisted or treated as first-party enterprise cloud traffic on managed
   Windows networks. Google Maps endpoints may be categorized differently.
4. **Different validation endpoints**: TowerScout validates Google against
   Static Maps and Geocoding on `maps.googleapis.com`. Azure validation checks
   Azure Maps attribution on `atlas.microsoft.com` and can fall back to Search.
   A network can block or inspect one set of endpoints but not the other.
5. **Different user path**: If the user mostly exercised Azure through the
   browser or through a validation endpoint that was not inspected, Azure will
   appear healthy while Google exposes the container trust gap.

The local evidence gathered during first-launch validation fits this model:
Google traffic was observed behind a managed TLS inspection chain, and Google
validation passed after the relevant inspection CA was imported into the
isolated Docker stack. That points to managed-network container trust, not a bad
Google key or unresolved Setup Wizard defect.

## Why Importing The CA Is The Correct Secure Fix

Python Requests verifies HTTPS certificates by default and allows applications
to specify a CA bundle through `verify` or `REQUESTS_CA_BUNDLE`. Requests also
warns that disabling verification accepts any certificate and makes the
application vulnerable to man-in-the-middle attacks.

Docker's own guidance for corporate HTTPS inspection is the same basic model:
the host and the containers/images that make network requests need to trust the
proxy's CA certificate. Docker also cautions that MITM CA certificates should be
handled carefully because a compromised inspection CA can intercept sensitive
data.

For TowerScout, importing the organization CA into a container-visible bundle is
the right balance:

- It keeps TLS verification enabled.
- It fixes provider validation and runtime provider calls, not only the Setup
  Wizard.
- It does not require the user to send API keys or raw network traces to
  support.
- It is engine-scoped, so Docker and Podman can be repaired independently.
- It avoids baking one organization's CA into a public release image.

## Current Mitigation

The current support command is:

```powershell
.\scripts\import-tls-ca.cmd -Engine docker -Gpu on -Thumbprint <windows-certificate-thumbprint> -VerifyProvider google
```

For CPU Docker, omit `-Gpu on`. For Podman, use `-Engine podman`. For
Azure-first or Google-blocked sites, use `-VerifyProvider azure` or
`-VerifyProvider none` when support intentionally wants to build the bundle
without a remote provider probe.

Expected result:

1. The helper exports the selected Windows certificate and chain.
2. It builds `/app/webapp/config/certs/towerscout-ca-bundle.pem` inside the
   selected engine's config volume.
3. It updates `.env` with:

```text
REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem
SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem
```

4. TowerScout is restarted.
5. Google validation reaches the provider and returns normal provider feedback
   instead of a TLS certificate verification failure.

## Options To Avoid This As A User-Facing Issue

### Option 1: Improve The Existing CA Import UX

Keep the current security model, but make the diagnosis/import path guided.

Possible implementation:

- Add `scripts/diagnose-tls-ca.ps1` or extend `scripts/import-tls-ca.ps1` with a
  discovery mode.
- Probe `maps.googleapis.com` without a real API key.
- Print the observed certificate issuer/subject chain.
- Search the Windows certificate stores for matching issuer/root candidates.
- Recommend one or more thumbprints with clear labels.
- Optionally import the selected candidate after explicit confirmation.
- Never print provider keys, full request URLs with keys, or raw network traces.

Benefits:

- Preserves secure TLS verification.
- Fixes all container-side provider calls.
- Reduces support friction.
- Does not change provider architecture.

Costs:

- Still requires a repair step on inspected networks.
- Needs careful certificate-selection UX to avoid trusting the wrong CA.

Recommendation: implement first. This is the lowest-risk product improvement.

### Option 2: Setup Wizard TLS Failure Triage

Make the Setup Wizard recognize provider TLS failures and show a targeted next
action.

Possible implementation:

- Detect `SSLError`, missing bundle, or unusable bundle cases.
- Return a structured error code such as `tls_ca_untrusted` or
  `tls_bundle_missing`.
- Show support-safe copy that says the key may be valid but the container does
  not trust the managed-network TLS inspection CA.
- Link to the import command or launch the guided helper when available.

Benefits:

- Users no longer interpret the failure as "Google rejected my key."
- Support gets a clear branch in the troubleshooting tree.

Costs:

- This improves diagnosis only. The container still needs the CA bundle before
  Google provider calls can succeed.

Recommendation: pair with Option 1.

### Option 3: Bootstrap/Preflight TLS Readiness Check

Run a provider TLS preflight before the user enters a real provider key.

Possible implementation:

- During `bootstrap.cmd` or `start.bat`, optionally test TLS to provider hosts
  with no key or an invalid key.
- If the response fails at TLS, recommend the CA import path.
- If TLS succeeds, continue without touching provider configuration.

Benefits:

- Finds the issue before the Setup Wizard.
- Does not require handling a real provider key.

Costs:

- Requires outbound network access during preflight.
- Needs provider-specific logic and a skip mode for offline or blocked sites.

Recommendation: useful after the guided import helper exists.

### Option 4: Host-Side Validation Only

Validate the Google key from Windows instead of from the container.

Possible implementation:

- A PowerShell/.NET helper uses the Windows trust store to call Google provider
  endpoints.
- The Setup Wizard accepts the result as key validation evidence.

Benefits:

- May avoid the immediate Setup Wizard failure.
- Uses the same trust store as the browser.

Costs:

- Does not fix container-side runtime calls for geocoding, static imagery, or
  other provider requests.
- Can create a false positive: setup passes, but detection/geocoding fails
  later inside the container.
- Adds another code path for provider validation.

Recommendation: diagnostic only, not a product fix.

### Option 5: Browser-Side Google Validation

Use the browser to validate Google Maps JavaScript or Places behavior.

Benefits:

- Uses Windows/browser trust.
- Can diagnose browser API restrictions and referrer restrictions.

Costs:

- Does not validate server-side Static Maps or Geocoding calls.
- Google Maps Platform keys need API and application restrictions appropriate
  to the APIs being used. A browser-restricted Maps JavaScript key is not the
  same thing as validating every server-side REST call TowerScout makes.

Recommendation: useful for key-restriction diagnosis, not a replacement for
container TLS trust.

### Option 6: Split Google Keys By Use

Use separate Google keys for browser SDK usage and server-side REST usage.

Benefits:

- Aligns with Google key-security guidance.
- Reduces blast radius if a client-visible key is abused.
- Makes API restrictions clearer.

Costs:

- Does not solve TLS trust.
- Adds setup complexity.

Recommendation: good security hardening, but not the answer to this TLS issue.

### Option 7: Host-Side Provider Proxy

Move all provider REST calls out of the container into a Windows helper service.
The container would call the local helper, and the helper would use Windows
trust.

Benefits:

- Avoids importing enterprise CA material into the container.
- Centralizes provider calls on the host trust store.

Costs:

- Significant new architecture: local service lifecycle, port binding,
  authentication, firewall behavior, request allowlisting, rate limiting,
  logging redaction, installer/service management, and failure recovery.
- Provider keys would be handled by another process.
- The helper must prevent arbitrary proxying and must avoid leaking keys in
  logs or diagnostics.
- Still needs TLS/proxy handling for the helper itself.

Recommendation: only consider if "no container CA import ever" becomes a hard
product requirement. It is not the right first fix.

### Option 8: Bake Organization CA Into A Custom Image

Produce a site-specific image containing the organization's CA.

Benefits:

- No post-start CA import for that organization.
- Standard Linux CA tooling can handle the trust store at build time.

Costs:

- Not viable for a public/general release image.
- Requires image rebuilds when the organization rotates inspection CAs.
- Broadens trust for every deployment using that custom image.
- Adds provenance, support, and release-management burden.

Recommendation: possible for a controlled enterprise deployment, not for the
general pilot package.

### Option 9: Disable TLS Verification

Use `TOWERSCOUT_ALLOW_INSECURE_TLS=1`.

Benefits:

- Fast diagnostic confirmation that the failure is certificate verification.

Costs:

- Accepts any certificate for provider validation.
- Weakens protection for provider keys and provider traffic.
- Should not be normal release posture.

Recommendation: keep as last-resort local troubleshooting only.

## Recommended Product Plan

### Phase 1: Make The Current Fix Easier

Add a guided TLS diagnosis/import workflow.

Acceptance criteria:

- The helper can inspect Google and Azure provider TLS without a real provider
  key.
- It can list candidate Windows certificate-store matches.
- It imports only after an explicit user/support selection.
- It updates the selected engine's config volume and `.env` exactly as the
  current helper does.
- It prints support-safe output with no API keys and no raw provider URLs
  containing keys.

### Phase 2: Surface A Better Setup Wizard Error

Return structured provider validation errors for TLS conditions.

Acceptance criteria:

- TLS inspection cases are distinguished from invalid-key cases.
- Missing or unusable CA bundle paths are distinguished from untrusted-chain
  failures.
- The user-facing copy says the provider key may be valid and points to the
  CA-import repair path.

### Phase 3: Add Optional Preflight Detection

Add a preflight check that can tell users up front whether provider TLS trust is
likely to fail.

Acceptance criteria:

- It works without provider keys.
- It can be skipped for blocked/offline networks.
- It reports Google and Azure independently.

### Phase 4: Revisit Architecture Only If Required

If the product requirement becomes "users must never import an enterprise CA
into the container," evaluate a host-side provider proxy. Treat that as a new
design, not a small fix.

## Security Boundaries

Provider keys and TLS diagnostics are sensitive enough to require strict
handling:

- Do not ask users to paste Google or Azure keys into support channels.
- Do not include keys in logs, screenshots, or evidence bundles.
- Do not print full provider URLs with `key=` or `subscription-key=` values.
- Do not import the Google website leaf certificate. Import the organization
  root or intermediate CA that signs the inspected chain.
- Do not silently trust arbitrary certificates observed on the wire.
- Do not use insecure TLS bypass except for bounded local troubleshooting.

## Open Questions

1. Should the guided helper be a new `diagnose-tls-ca` command or an extension
   of `import-tls-ca`?
2. Should Setup Wizard be allowed to launch the helper, or should it only print
   the support command?
3. Should TowerScout eventually support separate Google browser and server keys
   in the UI?
4. Do pilot sites want Azure-first provider guidance on managed networks where
   Google is inspected or blocked more aggressively?
5. Should support evidence include a redacted provider TLS summary artifact
   showing only host, issuer organization, and result?

## References

- Requests SSL certificate verification and `REQUESTS_CA_BUNDLE`:
  https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
- Docker CA certificates for corporate HTTPS inspection:
  https://docs.docker.com/engine/network/ca-certs/
- Google Maps Platform API key security guidance:
  https://developers.google.com/maps/api-security-best-practices
- Azure Maps authentication options and shared-key handling:
  https://learn.microsoft.com/en-us/azure/azure-maps/azure-maps-authentication
- TowerScout runtime TLS contract:
  `docs/support/oci-runtime-contract.md`
- TowerScout TLS import helper:
  `scripts/import-tls-ca.ps1`
