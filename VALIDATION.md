# Validation record

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
