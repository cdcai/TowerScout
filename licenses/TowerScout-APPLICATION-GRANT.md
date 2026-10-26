# TowerScout application and supporting-material license grant

The project-controlled TowerScout application code inventoried below, including
inherited CC-marked code, its modifications and extracted application modules,
is additionally licensed under the **GNU Affero General Public License,
version 3 (AGPL-3.0-only)**. This project-owner-approved grant is effective
October 23, 2026. The approved scope clarification of October 25, 2026 also
covers project-controlled supporting code and accompanying documentation in
this release's corresponding source. See [the complete AGPL text](AGPL-3.0.txt) and [source identity](../SOURCE.txt).

Recipients may use, modify and distribute this covered application code under
AGPL-3.0 without also applying the CC noncommercial/share-alike conditions to
that AGPL-licensed use. Previously granted CC-BY-NC-SA-4.0 permissions remain
available as an alternative; they are not revoked. Existing Apache-2.0 grants
also remain available where applicable. This does not newly offer inherited
CC-covered material under Apache-2.0.

Retain original authorship and attribution, including Karen Wong, Gunnar Mein,
Thaddeus Segura, Jia Lu and the TowerScout team, together with applicable
contributor notices. The generated frontend carries this grant through its
listed source inputs. The applicable license supplies its warranty disclaimer
and limitations of liability.

## Scope and exclusions

This grant covers project-controlled application code, supporting code and
accompanying documentation shipped in this source revision. Supporting material
includes the Docker/Compose build files, Windows launch/package/maintenance
scripts, CI workflows, tests, repository development configuration and retained
project skills, and project documentation. The application inventory below is
a coverage record of this revision, not a separate approval requirement for
each extracted application module. Existing grants and upstream notices within
mixed-source files remain effective.
It does not relicense third-party material, including `webapp/vendor/`, jQuery,
installed dependencies, provider SDKs/services, model weights or data. Research
materials under `Model/` and `SyntheticData/`, and the historical website
excluded from this release, are outside this grant. Existing third-party notices
remain effective, including within a listed file. This grant does not assert
new rights over third-party artwork or other excluded material.

The EfficientNet classifier **weights** retain CC-BY-NC-SA-4.0. The grant covers
the TowerScout `ts_en.py` application wrapper, not those weights or the separately
licensed EfficientNet implementation. See the [root license](../LICENSE),
[model notices](../MODEL_LICENSES.md) and [third-party notices](../THIRD_PARTY_NOTICES.md).
The full model-enabled distribution must not be described as unrestricted or
entirely AGPL-licensed. Existing [CC](CC-BY-NC-SA-4.0.txt) and
[Apache](Apache-2.0.txt) texts remain supplied.

## Covered application paths

Paths are relative to the corresponding-source repository root. They identify
the code accompanying this grant, not an automatic grant over future additions.

```text
webapp/build.js
webapp/css/ts_styles.css
webapp/css/ts_styles_mobile.css
webapp/js/azure_maps_debug.js
webapp/js/src/boundaries/CircleBoundary.js
webapp/js/src/boundaries/PolygonBoundary.js
webapp/js/src/boundaries/ZipcodeBoundary.js
webapp/js/src/config.js
webapp/js/src/detection/Detection.js
webapp/js/src/detection/DetectionList.js
webapp/js/src/detection/DetectionReview.js
webapp/js/src/detection/PlaceRect.js
webapp/js/src/detection/Tile.js
webapp/js/src/globals.js
webapp/js/src/managers/ErrorHandler.js
webapp/js/src/managers/EventListenerManager.js
webapp/js/src/managers/ProviderStateManager.js
webapp/js/src/managers/TimerManager.js
webapp/js/src/providers/AzureMap.js
webapp/js/src/providers/GoogleMap.js
webapp/js/src/providers/TSMap_base.js
webapp/js/src/providers/providerInit.js
webapp/js/src/providers/providerSwitch.js
webapp/js/src/settings.js
webapp/js/src/setup-wizard.js
webapp/js/src/store.js
webapp/js/src/towerscout.js
webapp/js/src/ui/export.js
webapp/js/src/ui/navigation.js
webapp/js/src/ui/search.js
webapp/js/src/utils/apiHelpers.js
webapp/js/src/utils/coordinates.js
webapp/js/src/utils/imagery.js
webapp/js/src/utils/polygonValidation.js
webapp/js/towerscout.js
webapp/js/towerscout.original.js
webapp/static/phase1_validation.js
webapp/templates/incompatible.html
webapp/templates/towerscout.html
webapp/templates/unauthorized.html
webapp/towerscout.py
webapp/ts_assets.py
webapp/ts_azure_maps.py
webapp/ts_config.py
webapp/ts_dataset.py
webapp/ts_device.py
webapp/ts_en.py
webapp/ts_errors.py
webapp/ts_events.py
webapp/ts_geocache.py
webapp/ts_geocoding.py
webapp/ts_gmaps.py
webapp/ts_host_helper.py
webapp/ts_imgutil.py
webapp/ts_logging.py
webapp/ts_maps.py
webapp/ts_paths.py
webapp/ts_performance.py
webapp/ts_progress.py
webapp/ts_provider_http.py
webapp/ts_runtime.py
webapp/ts_tls.py
webapp/ts_trust.py
webapp/ts_validation.py
webapp/ts_yolov5.py
webapp/ts_yolov5_local.py
webapp/ts_zipcode.py
```
