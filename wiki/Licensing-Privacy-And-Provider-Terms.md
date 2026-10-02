# Licensing, Privacy, And Provider Terms

> **Audience:** Users, Local IT, and maintainers. **Applies to:** The selected
> final release. **Last reviewed:** 2026-10-02. **Publication state:** Local
> draft.

TowerScout's source license does not grant permission to use Google Maps,
Azure Maps, model/data inputs, or third-party components outside their own
terms. Review the version-matched notices shipped with the Application Package:

- `LICENSE` and `NOTICE`;
- `THIRD_PARTY_NOTICES.md`;
- `MODEL_LICENSES.md` and `DATA_LICENSES.md`;
- `PROVIDER_TERMS.md`;
- `SOURCE.txt`; and
- the release SBOM when provided.

The running application exposes formatted notices at `/license` and plain text
at `/license.txt` on its local address.

Provider services are separate from TowerScout. The user/site owns the
provider account, billing, allowed-use decision, quotas, monitoring, and
credential rotation. TowerScout currently exposes its configured provider key
to browser code and uses the same credential for application requests; use a
dedicated limited account/key and follow
[Google And Azure API Credentials](Google-And-Azure-API-Credentials).

Search areas, uploaded images, cached provider responses, session data, logs,
and exports may reveal sensitive locations or investigations. Keep them under
the site's approved access, retention, backup, and deletion procedures. Do not
place them in a public issue, screenshot, demo, browser trace, or release
artifact.
