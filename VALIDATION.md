# Validation record

## Nature extension added 2026-11-05

The repository contains **18 notebooks**, including four Nature chapters (14–17). All 18 executed in fresh desktop kernels during the build; the four Nature notebooks were executed again after review fixes. **41 tests passed**, covering existing behavior and the new datum equation, asymmetric comparison matrices, cohort conservation, NoData/exclusion thresholds, raster CRS/band/scale/offset, failed coordinate transformations, manifest validation, terrain provenance and CSV upload-state cleanup.

The local source workbook contains 58,731 rows, of which **25,873** have `PEPFARSUP = 1`. Their unique identifiers and coordinates were validated, and all **24** original RCP category totals match the poster. The real sampling run used one global GLL coastal-lowland grid and **13 FABDEM / 12 DeltaDTM tiles** selected around five public poster-city anchors. Publisher SHA-256 verified the original GLL download; original SHA-256 values for the selected regional tiles were calculated and pinned after download. All 26 retained compressed raster hashes were checked against the acquisition inventory. The catalog distinguishes publisher checksums from locally computed hashes.

Valid facility samples: **798 GLL, 694 FABDEM, 692 DeltaDTM**. The common valid cohort has **207** facilities; at ≤1 m MSL the counts are **25, 9, 35**, respectively. An independent pandas recount from the private sampled rows verified all nine screening totals, three common-cohort comparisons and **216 RCP overlap matrices**. Missing and outside-coverage rows remain unavailable. The original elevation quality audit records **20,476 zero values**, whose fill/unassessed semantics remain unresolved; the primary historical comparisons use the audited RCP flags. Private sample rows and workbook audits remain in ignored `private-data/`; a scan of 45 public content/reference files found none of the source facility identifiers.

Three independent review lenses produced 20 findings, including duplicates. All were addressed; no review finding was deferred. Public city terrain excerpts retain the same 15 numeric grids after the band-decoding/provenance fixes, and encoded-band fixtures verify the additional supported inputs. Static book terrain heatmap and 3D surface rendering were visually inspected in Chromium.

The final book built with warnings treated as errors; JupyterLite validation passed, and all required assets/internal links passed across **29 authored/book pages**. Chromium checks passed for all four new Pyodide notebooks and the six representative existing chapters (00, 01, 05, 07, 09, 13). New interactions checked actual values: city/model changes replaced the complete heatmap and 3D surface arrays; model/threshold changes updated count, coverage and bars; the sensitivity slider updated its selected point; a synthetic CSV replaced the demo; an invalid replacement retained the prior valid data; restore returned to the default fictional counts. The existing dashboard's filters, CSV export, 3D views and responsive layouts also passed. Power BI rendering remains mocked as described below.

The initial browser harness was corrected to wait for explicit notebook readiness rather than background network inactivity, and to use the widget's real file chooser. These were test-harness fixes; all affected browser checks passed afterward. Git-staged bytes matched all 23 public-artifact hashes and the terrain-generator hash, including Windows/Linux newline normalization.

This is a **facility point-sampling adaptation with partial coverage**, not a reproduction of the paper's global population analysis or hydrodynamic flood modeling. High-resolution tiles are a purposive five-region sample, not a representative global facility sample. GLL is about 1 km; high-resolution sampling uses native approximately 30 m cells. The separate city display grids are sparsely sampled and rounded for teaching and never used for facility classification. Absolute counts across unmatched model footprints must not be ranked. No new RCP/year flood probabilities or inundation footprints are estimated.

Reproduce the new checks and local analysis with:

```bash
python -m pip install -r requirements.txt -r requirements-geospatial.txt
python -m pytest tests -q
python scripts/nature_lessons.py
python scripts/build.py
python scripts/check_site.py
# Optional public-only acquisition; about 4 GB transferred, no facility inputs:
python scripts/fetch_nature_rasters.py
# Authorized local workbook, never committed:
python scripts/analyze_nature.py private-data/sites.xlsx --manifest private-data/nature-download/manifest.json
python scripts/prepare_nature_surfaces.py --manifest private-data/nature-download/manifest.json
python scripts/update_provenance.py
```

Actual acquisition used two public-only GitHub Actions runs recorded in `content/data/nature-raster-catalog.json`, because the source's port 9443 was unavailable locally. The consolidated optional download script packages the same URL/checksum/compression procedure; ordinary builds and browser notebooks do not launch raster downloads.

## Power BI chapter added 2026-10-05

The repository now contains 14 notebooks. Chapter 13 executed successfully in desktop Python and in a real JupyterLite/Pyodide browser kernel with `python-power-bi==0.1.2`. All 21 unit tests passed (the original six plus 15 Power BI metadata/URL cases), including separate commercial and GCC routing. The book built with warnings treated as errors, and 25 authored/book HTML pages passed internal-link and asset checks.

The browser check verifies the actual package's metadata exercise, the prefilled user-supplied GCC URL, URL rejection, the original RCP 8.5 page selection, and the iframe/new-tab integration. Power BI requests are intercepted with an explicitly labeled mock frame. **This does not verify a real tenant login or original-report rendering.** The user supplied the hosted report URL; an authenticated browser session is unavailable in this environment, and the web reader cannot access that report. Running cells alone never requests credentials, uploads the PBIX or contacts Power BI; selecting **View report** opens Microsoft's sign-in/viewer. The historical chapter checks below were recorded on 2026-10-04; CI reruns them with the new chapter.

To test only the new browser notebook:

```bash
python scripts/lite_smoke.py --url http://127.0.0.1:8769 --notebooks 13_powerbi_in_browser
```

## Original learning-site validation

Validated locally on **2026-10-04**, Python 3.13, Chromium through Playwright, Jupyter Book 1.0.4.post1, JupyterLite 0.8.5 and Pyodide kernel extension 0.8.6. The GitHub workflow repeats the build/data/browser checks before publishing. See the Actions badge in the README for the current deployment result.

| Check | Result |
|---|---|
| All 13 notebooks executed from a fresh kernel | Passed; no cell errors |
| Six scientific/data-integrity tests | Passed: public totals, reporting keys, denominators, panel completeness, duplicate rejection, filter/card reconciliation, probability edges, synthetic IDs, asset hashes |
| Jupyter Book build with warnings as errors | Passed |
| JupyterLite schema/content checks | Passed; 13 notebooks indexed, Python kernel and widgets bundled |
| Built internal links and required assets | Passed across 24 authored/book HTML pages |
| Desktop browser dashboard | Passed: all three RCP tabs, 2030/2100 public totals, country/city scope, CSV export, fictional cohort and threshold checks |
| Responsive dashboard | Passed at 1440 px and 390 px; plot widths follow container widths after resize |
| Browser 3D modes | Geographic stems, space–time cube and fictional terrain rendered in Chromium with software WebGL available |
| Book interactive figure | Plotly iframe rendered using the locally bundled chart library; no page JavaScript errors |
| Actual JupyterLite/Pyodide execution | Chapters 00, 01, 05, 07 and 09 ran successfully in the browser, including data reads, embedded dashboard, Plotly, ipywidgets, NumPy/Pandas and permutation calculations |
| Visual inspection | Official poster preview, comic, landing page, dashboard desktop/mobile, 3D scene, book and live notebook inspected |
| Published study consistency | All 24 whole-portfolio counts independently matched the supplied workbook; city/district rows visually transcribed from the official poster |

## Reproduce the checks

```bash
python -m pip install -r requirements-test.txt
python -m pytest tests/test_science.py -q
python scripts/build.py
python scripts/check_site.py
python -m playwright install chromium
python -m http.server 8769 --directory _site --bind 127.0.0.1
# In another terminal:
python scripts/browser_smoke.py --url http://127.0.0.1:8769
python scripts/lite_smoke.py --url http://127.0.0.1:8769
```

The browser checks save screenshots and a small results record under ignored `tmp/browser/`. The optional local private-workbook audit emits only pass/fail against already-public totals; it is not part of public CI.

## Practical limits

Browser execution was checked in Chromium, not every browser/device. Pyodide and Python-package downloads need network access on first use; browser-side package versions can differ from desktop versions. This is not a fully offline distribution. WebGL availability varies; tables, 2D charts and the static book remain the reading alternatives.

The synthetic model, terrain, scan experiment and service-capacity examples are instructional, not validated hazard or clinical models. No scientific replication claim is made for CoastalDEM/PAT processing or the original SaTScan settings. External historical source URLs can move; they are distinguished from internal links checked by the build. The source audit documents numeric/wording discrepancies rather than hiding them.
