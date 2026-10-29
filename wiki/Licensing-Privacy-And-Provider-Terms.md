# Licensing, Privacy, And Provider Terms

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

TowerScout's source license does not grant permission to use Google Maps,
Azure Maps, model/data inputs, or third-party components outside their own
terms. Review the version-matched notices shipped with the Application Package:

- [Application license](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/LICENSE) and [notices](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/NOTICE);
- [Third-party notices](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/THIRD_PARTY_NOTICES.md);
- [Model terms](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/MODEL_LICENSES.md) and [data terms](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/DATA_LICENSES.md);
- [Provider terms](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/PROVIDER_TERMS.md);
- [Corresponding source](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/SOURCE.txt); and
- [Software inventory (SBOM) references](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/SBOM.txt).

Model weights have separate terms, including CC-BY-NC-SA-4.0 for the
EfficientNet classifier weights. The linked model notices identify the
applicable terms; the application grant does not replace them.

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

Documentation provenance and public attribution remain in the [exact corresponding source](https://github.com/cdcai/TowerScout/tree/412411786f24b3dddda02506ca44bf9b77f9874d) and [supporting-material grant](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/licenses/TowerScout-APPLICATION-GRANT.md). The [complete applicable AGPL text](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/licenses/AGPL-3.0.txt) is available with that source; model/data/provider and third-party terms remain separate.
