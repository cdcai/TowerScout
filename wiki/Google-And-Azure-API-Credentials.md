# Google And Azure API Credentials

> **Audience:** End users and Local IT. **Applies to:** The selected provider
> and its current terms. **Last reviewed:** 2026-10-02. **Publication state:**
> Local draft.

TowerScout needs one approved Google Maps or Azure Maps credential. Provider
services, enrollment, billing, quotas, and usage rights are not included with
TowerScout.

## Ownership And Restrictions

- Use a site/user-owned key approved for this workstation and purpose.
- Restrict enabled APIs, HTTP referrers/origins, quotas, and usage alerts as
  narrowly as the provider and deployment allow.
- Use separate browser and server credentials where the provider supports that
  model.
- Monitor usage and follow the provider/site incident-response process for
  suspected exposure.

Official security guidance:

- [Google Maps Platform API security best practices](https://developers.google.com/maps/api-security-best-practices)
- [Azure Maps authentication best practices](https://learn.microsoft.com/en-us/azure/azure-maps/authentication-best-practices)

## Browser Visibility

Google and Azure browser SDK keys are client-visible by provider design. A
person who can inspect the running browser may be able to see the browser key.
Treat restrictions, quota controls, monitoring, and workstation access as part
of the security model; do not describe a browser SDK key as secret from the
browser.

## Safe Handling

Enter the key privately through TowerScout Setup Wizard or Settings. Never:

- commit it or include it in a package;
- paste it into an issue, chat, email, or public support record;
- show it in screenshots, video, raw logs, `.env`, or browser traces; or
- copy it between isolated test profiles without explicit site approval.

If validation fails, report the provider label and sanitized error category,
not the key or provider response body. TLS-inspection problems can be diagnosed
without giving support the provider key.
