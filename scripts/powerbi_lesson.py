"""Author chapter 13 independently, or as part of make_notebooks.py."""
from pathlib import Path
import json
import textwrap
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
SLUG = '13_powerbi_in_browser'
TITLE = 'Open the original Power BI report in the browser'


def make_notebook():
    def md(s): return nb.v4.new_markdown_cell(textwrap.dedent(s).strip())
    def code(s): return nb.v4.new_code_cell(textwrap.dedent(s).strip())
    cells = [md('''
    # Open the original Power BI report in the browser

    **Time:** 30 minutes · **Prerequisites:** a published report URL and Power BI viewing permission for the live report. The offline API exercise needs neither.

    [Run in JupyterLite](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/lite/lab/index.html?path=notebooks/13_powerbi_in_browser.ipynb) · [Public teaching dashboard](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/dashboard/)

    Learn what `python-power-bi` does, inspect the supplied report's page structure, and open the original interactive report with its RCP tabs, slicers, maps and cards.

    **Connection status:** No Power BI Service URL was supplied with the PBIX. This notebook is ready to accept one; it does not claim the original report is already hosted or connected.

    Wait for **Python (Pyodide) | Idle**, then use **Run → Run All Cells**. First use downloads packages. The default run performs an offline metadata exercise and displays connection controls. It does not upload the PBIX or sign in automatically.
    '''), md('''
    ## 1. A PBIX file, an API client and a report viewer

    | Component | Its job here |
    |---|---|
    | `Prototype-July-8-2024.pbix` | Original Power BI Desktop artifact; inspected locally, not bundled in this public repository |
    | Power BI Service | Hosts the published report and executes its model and visuals |
    | `python-power-bi==0.1.2` | Unofficial Python REST API wrapper; retrieves report/page metadata; not a PBIX renderer |
    | Secure Power BI iframe | Displays Microsoft's report viewer in this notebook; sign-in and permissions remain with Microsoft |
    | JupyterLite | Runs the Python exercise and notebook controls in your browser |

    The [package](https://pypi.org/project/python-power-bi/) and its `Reports` methods do not provide a local PBIX execution engine. Putting the PBIX on GitHub or installing a Python package does not make the original model run in WebAssembly. The repository's teaching dashboard is a separate implementation; this chapter connects to the original report instead.

    We pin the **PyPI 0.1.2 wheel**, whose method names differ from newer code on the upstream repository's main branch. The notebook uses the actual package, with an explicitly labeled no-network transport for the first exercise.

    **Other packages:** Microsoft's [`powerbiclient`](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/powerbi-jupyter) provides a Jupyter widget for embedding hosted reports and controlling filters/bookmarks. It still requires a hosted report; its custom widget/authentication stack is not tested in this JupyterLite deployment. [`PBIXRay`](https://pypi.org/project/pbixray/) reads local model data and metadata but does not evaluate DAX or render the report layer. Recreating visuals from extracted, approved data is a separate workflow, like the existing Plotly teaching dashboard.
    '''), code('''
    import sys
    from pathlib import Path
    if sys.platform == 'emscripten':
        import piplite
        # This browser lesson uses Reports + requests; server authentication is optional.
        await piplite.install(['requests', 'ipywidgets'])
        await piplite.install('python-power-bi==0.1.2', deps=False)
    from importlib.metadata import version
    from IPython.display import display, display_html
    from powerbi.reports import Reports
    import json

    root = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
    sys.path.insert(0, str(root))
    from powerbi_bridge import (report_config, MetadataFixture, DEMO_WORKSPACE, DEMO_REPORT,
                               report_identity, secure_embed_url, embed_markup,
                               report_viewer, lookup_live_metadata)
    config = report_config()
    assert version('python-power-bi') == '0.1.2'
    print('Ready: python-power-bi 0.1.2; offline metadata exercise + secure report viewer.')
    '''), md('''
    ## 2. Use the actual package without an account

    The transport below returns a **fixture**, not a response from Microsoft. The report/workspace GUIDs are dummy identifiers. Page names and captions come from `Report/Layout` in the supplied PBIX; no facility records or coordinates were extracted into this fixture. Request paths are shown so you can see precisely what the library would ask the service for.
    '''), code('''
    fixture = MetadataFixture(config['pages'])
    reports = Reports(session=fixture)
    demo_report = reports.get_group_report(group_id=DEMO_WORKSPACE, report_id=DEMO_REPORT)
    demo_pages = reports.get_group_pages(group_id=DEMO_WORKSPACE, report_id=DEMO_REPORT)['value']
    print('OFFLINE FIXTURE — no Power BI API request or sign-in occurred.')
    print(demo_report['name'])
    for page in demo_pages:
        print(f"{page['ordinal']:02d}  {page['displayName']}  ->  {page['name']}")
    print(json.dumps(fixture.calls, indent=2))
    assert len(demo_pages) == 18
    assert len([p for p in demo_pages if p['displayName'].startswith('RESULTS RCP')]) == 3
    '''), md('''
    ## 3. Publish once, then use the browser viewer

    If the report is already in Power BI Service, copy **File → Embed report → Website or portal** (the URL, not the entire iframe), or its `/groups/.../reports/...` address. If it is not hosted yet, open the PBIX in Power BI Desktop, choose **Publish**, and select your approved workspace. See Microsoft's [publishing instructions](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-upload-desktop-files).

    This study's facility data have provider access conditions. Use the authenticated **Website or portal** route; **Publish to web** makes content publicly accessible and is not the route used here. The PBIX is not uploaded by this notebook. [Publish-to-web behavior](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web).

    Paste the report URL below, select an RCP or another page, and click **View report**. Sign in inside Microsoft's viewer. The report's own slicers, maps, card aggregations and line listings then operate normally. The page selector uses internal PBIX page names; refresh the metadata if those pages were recreated after publication.

    Secure embedding preserves report permissions and RLS. It does not grant access. Viewers need the applicable Power BI license or qualifying hosting capacity. If sign-in is blocked by pop-up/cookie rules or the notebook frame, use **Open this report in a new tab**. See [Microsoft's secure embedding guide](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-embed-secure).
    '''), code('''
    # A report URL is not an access token. Never paste credentials here.
    REPORT_URL = config.get('report_url', '')
    viewer = report_viewer(REPORT_URL, pages=config['pages'])
    '''), md('''
    ## 4. Inspect a page link without opening a dummy report

    URL parameters select the starting page; they are not access controls. This example builds a link using the dummy report identifier and the original RCP 8.5 page name, then validates it without sending any request.
    '''), code('''
    rcp85_page = next(p['name'] for p in demo_pages if p['displayName'] == 'RESULTS RCP 8.5 (C)')
    example_url = secure_embed_url(demo_report['embedUrl'], rcp85_page)
    from urllib.parse import parse_qs, urlsplit
    assert parse_qs(urlsplit(example_url).query)['pageName'] == [rcp85_page]
    assert report_identity(example_url)['report_id'] == DEMO_REPORT
    print('Link-building check passed. Dummy link was not opened.')
    '''), md('''
    ## 5. Optional: discover the live pages with python-power-bi

    This step runs in **local/server Jupyter**, not JupyterLite. Install `python-power-bi==0.1.2`, `msal` and `ipywidgets` in that kernel (the repository requirements include them). An administrator must provide an Entra public-client app registration with device-code flow enabled and delegated Power BI **Report.Read.All** permission/consent. Set `PBI_CLIENT_ID` and `PBI_TENANT_ID` in the local environment. Tenant policy can prohibit device-code sign-in; in that case use the secure report link from the service UI.

    Set `REPORT_URL` above to the workspace report URL, then deliberately enable the cell below. It signs in through MSAL and calls the package's `Reports.get_group_report()` / `get_group_pages()` methods (or `get_report()` / `get_pages()` for My Workspace). A small read-only transport sends those two GET requests with a timeout. Only metadata is retrieved. No PBIX import, dataset export or modification is performed.

    The package's `PowerBiClient` constructor uses a confidential-client authentication flow. We do not place that client secret flow in a public browser notebook. The optional local flow keeps tokens in memory and does not write a token cache. API sign-in does not sign you into the embedded viewer; the latter uses its own Microsoft browser session. [MSAL token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens) · [Report metadata API](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-report-in-group) · [Page metadata API](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-pages-in-group).
    '''), code('''
    ENABLE_LIVE_LOOKUP = False
    if ENABLE_LIVE_LOOKUP:
        if sys.platform == 'emscripten':
            print('Use local/server Jupyter for authenticated API lookup. The browser viewer above works with a secure report URL.')
        else:
            import os
            live_report, live_pages = lookup_live_metadata(
                REPORT_URL, os.environ['PBI_CLIENT_ID'], os.environ['PBI_TENANT_ID'])
            print('Live report/page metadata received. Facility data were not exported.')
            live_viewer = report_viewer(live_report['embedUrl'], pages=live_pages)
    else:
        print('Live API lookup disabled. No credentials requested and no report uploaded.')
    '''), md('''
    ## Lab: reproduce one observation using the original report

    1. Connect the published original report. Select **RESULTS RCP 2.6 (A)** and reset its slicers.
    2. Match the cohort, geographic scope and 2030 year to the poster before comparing a card to 108.
    3. Repeat for **RESULTS RCP 4.5 (B)** and **RESULTS RCP 8.5 (C)**. Inspect a map selection and a line listing to explain how cross-filtering changes the count.
    4. Compare 2030 and 2100. Record report refresh date, filters and denominator; a refreshed portfolio may differ from the historical poster.

    **Worked checks:** There are three RCP results pages. Their internal page names begin with `ReportSection`; the visible captions are not page IDs. With the original supported portfolio and matching filters, the historical 2100 poster totals are 321, 331 and 412. A login prompt or blank report is not a zero exposure count.

    **Deliverable:** A short reconciliation of one report card with a poster table row, including filters and any mismatch. If no hosted report is available, submit the offline request log and explain the hosting dependency; do not describe that exercise as a live report.

    ## Troubleshooting and attribution

    | Symptom | Check |
    |---|---|
    | Not connected | Supply the hosted report URL; a local PBIX path is not sufficient |
    | Sign-in or access denied | Microsoft account, report permission, tenant policy and licensing |
    | Blank iframe after sign-in | Open the generated new-tab link; allow the organization's required sign-in pop-ups |
    | Wrong page | Use the internal name from the current service report's page metadata |
    | API 401 / 403 | Sign-in/token lifetime, delegated API consent and permission on this report |
    | Unsupported URL | Use the commercial-cloud Website or portal URL; app short links and sovereign-cloud hosts are not implemented here |

    `python-power-bi` 0.1.2: Alex Reed, MIT (2020 notice retained in repository licenses). `msal` is Microsoft's MIT-licensed authentication library. Power BI is a Microsoft service governed by its own terms; the wrapper's MIT license grants no rights to report data. The page catalog is metadata from the user-supplied PBIX, inspected 2026-10-05. The original PEPFAR/PAT data rights still apply.

    Tested without tenant credentials: package imports, its two metadata methods with fixtures, page-link construction and notebook controls. Live tenant authentication and original-report rendering require a real hosted report and authorized account and are not verified by the offline checks.
    ''')]
    return nb.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python (Pyodide)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.13'},
        'coastal_futures': {'estimated_minutes': 30, 'evidence_layers': ['PBIX page metadata', 'offline API fixture', 'optional authenticated report']}})


def write_notebook():
    path = ROOT / 'content/notebooks' / (SLUG + '.ipynb')
    nb.write(make_notebook(), path)
    return SLUG, TITLE, 30


if __name__ == '__main__':
    write_notebook()
    index = ROOT / 'content/lesson-index.json'
    entries = json.loads(index.read_text(encoding='utf-8'))
    entries = [entry for entry in entries if entry['slug'] != SLUG]
    entries.append({'slug': SLUG, 'title': TITLE, 'minutes': 30})
    index.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Authored', SLUG)
