# Google And Azure API Credentials

> **Audience:** New users and Local IT. **Applies to:** The provider you choose
> and its current terms. **Last reviewed:** 2026-10-02. **Publication state:**
> Local draft; verify provider-console labels before final publication.

TowerScout needs one working Google Maps API key or one Azure Maps subscription
key. Provider accounts, billing, usage rights, and charges are not included
with TowerScout.

## Important Current Limitation

TowerScout currently accepts one credential for each provider and uses that
same credential for browser map display and application requests. Do not create
separate browser and server keys for TowerScout; there is only one field for
each provider. A person with access to the running browser may be able to see
the configured key.

Use a dedicated, least-privilege provider project/account with API restrictions,
quotas, alerts, monitoring, and a rotation plan. If your organization requires
separate browser/server credentials, Microsoft Entra ID, a secret that can
never be visible to the browser, or another stronger control, this release
does not meet that requirement.

## Option A: Google Maps

1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project owned by you or your organization.
3. Attach an approved billing account. Google Maps Platform may charge for
   usage; review current pricing and set budget/usage alerts.
4. Enable these APIs for the project:
   - Maps JavaScript API;
   - Maps Static API;
   - Geocoding API; and
   - Places API used by the Maps JavaScript Places library.
5. Open **Google Maps Platform > Credentials**, select **Create credentials >
   API key**, and give the key a TowerScout-specific name.
6. Apply **API restrictions** for only the four APIs above. TowerScout's
   current one-key design makes browser-referrer and server-side restrictions
   difficult to combine; use only an application restriction that your site
   has verified works for both TowerScout paths. Do not assume a referrer-only
   or IP-only rule will cover both.
7. Set quotas and alerts appropriate for local TowerScout use. Copy the key to
   a temporary private location for entry into TowerScout; do not put it in a
   document, screenshot, issue, or chat.

Official instructions:

- [Get started with Google Maps Platform](https://developers.google.com/maps/get-started)
- [Set up the Maps JavaScript API and create a key](https://developers.google.com/maps/documentation/javascript/get-api-key)
- [Google Maps Platform API security best practices](https://developers.google.com/maps/api-security-best-practices)

## Option B: Azure Maps

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. Use an Azure subscription and resource group owned by you or your
   organization. Review current pricing and approval requirements.
3. Search for **Azure Maps**, select **Create**, create an Azure Maps account,
   and accept the applicable terms. Use the current Gen2 pricing tier shown by
   Azure unless your organization directs otherwise.
4. Open the Azure Maps account. Under **Settings**, open **Authentication**.
5. Copy the **Primary Key** to a temporary private location for entry into
   TowerScout. Keep the Secondary Key available for controlled rotation.
6. Configure Azure budgets, quotas/alerts, monitoring, and key-rotation
   practices required by your organization.

TowerScout uses Azure Maps Web SDK, imagery/tile, search, and geocoding
requests. It currently supports the shared subscription-key method; Microsoft
recommends Microsoft Entra ID for production web applications, but TowerScout
does not currently expose that authentication option.

Official instructions:

- [Create an Azure Maps account and retrieve a key](https://learn.microsoft.com/azure/azure-maps/quick-demo-map-app)
- [Azure Maps authentication best practices](https://learn.microsoft.com/azure/azure-maps/authentication-best-practices)

## Enter And Validate The Credential

After TowerScout opens, its Setup Wizard shows separate Google and Azure key
fields. Paste only the provider credential you chose, select that provider as
the default, and choose **Validate** or save the setup as directed on screen.
One valid provider is enough.

If validation fails, do not post the key or a provider response. Use the
message category:

- **invalid key:** check for a copying error or rotate the key;
- **API not authorized:** enable the required service and review API
  restrictions;
- **billing/account:** confirm the provider account and billing status;
- **quota/rate limit:** review provider usage and quota controls; or
- **certificate/TLS:** ask Local IT to inspect the managed-network trust path.
