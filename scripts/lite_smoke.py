"""Run representative real notebooks in a headless browser's Pyodide kernel."""
from pathlib import Path
import argparse,json,time
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def expect_plot_values(page, output_class, traces):
    """Wait for the replacement iframe's actual Plotly data, not its label."""
    page.wait_for_function("""({selector, expected}) => {
        const frame = document.querySelector(selector);
        const plot = frame?.contentDocument?.querySelector('.js-plotly-plot');
        const actual = plot?._fullData;
        if (!actual || actual.length !== expected.length) return false;
        function equal(a, b) {
            if (Array.isArray(b)) return a != null && a.length === b.length && b.every((v, i) => equal(a[i], v));
            if (b === null) return a === null || !Number.isFinite(a);
            if (typeof b === 'number') return Number.isFinite(a) && Math.abs(a - b) < 1e-8;
            return a === b;
        }
        return expected.every((trace, i) => Object.entries(trace).every(([key, value]) => equal(actual[i][key], value)));
    }""",arg={'selector':f'.jp-Notebook .{output_class} iframe','expected':traces},timeout=60000)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8000')
    ap.add_argument('--notebooks',nargs='+',default=['00_start_here','01_read_the_poster','05_dashboard_lab','07_three_dimensions','09_hotspots','13_powerbi_in_browser','14_vertical_datums','15_nature_data_and_sampling','16_facility_comparison','17_datum_sensitivity'])
    args=ap.parse_args()
    out=ROOT/'tmp/browser';out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        context=browser.new_context(viewport={'width':1400,'height':1000})
        for slug in args.notebooks:
            print('RUN',slug,flush=True)
            started=time.monotonic();page=context.new_page();errors=[]
            powerbi_requests=[]
            if slug=='13_powerbi_in_browser':
                def mock_powerbi(route):
                    powerbi_requests.append(route.request.url)
                    route.fulfill(status=200,content_type='text/html',body='<p>Mock Power BI frame for interface test</p>')
                page.route('https://app.powerbi.com/**',mock_powerbi)
                page.route('https://app.powerbigov.us/**',mock_powerbi)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(args.url+f'/lite/lab/index.html?path=notebooks/{slug}.ipynb',wait_until='domcontentloaded',timeout=60000)
            page.get_by_role('tab',name=slug+'.ipynb',exact=True).click(timeout=60000)
            page.wait_for_selector('.jp-Notebook:visible',timeout=60000)
            # Wait for Pyodide before sending execution requests. Clicking Run during
            # session creation can race the kernel chooser and discard that request.
            page.wait_for_function("() => document.querySelector('[role=dialog]') || [...document.querySelectorAll('.jp-KernelStatus-success')].some(e=>e.offsetParent!==null)",timeout=180000)
            if page.get_by_role('dialog').count():
                page.get_by_role('button',name='Select',exact=True).click()
            page.wait_for_selector('.jp-KernelStatus-success:visible',timeout=180000)
            page.get_by_role('menuitem',name='Run',exact=True).click();page.get_by_role('menuitem',name='Run All Cells',exact=True).click()
            nature = slug.startswith(('14_', '15_', '16_', '17_'))
            ready='Ready: Nature 2026' if nature else 'Ready: python-power-bi 0.1.2' if slug=='13_powerbi_in_browser' else 'Ready: public poster'
            page.wait_for_function("ready => [...[...document.querySelectorAll('.jp-Notebook')].find(n=>n.offsetParent!==null).querySelectorAll('.jp-OutputArea-output')].some(e=>e.textContent.includes(ready))",arg=ready,timeout=180000)
            # Notebook virtualization is disabled in overrides.json; reveal the final cell.
            last=page.locator('.jp-Notebook:visible .jp-Cell').last
            last.scroll_into_view_if_needed()
            if nature:
                marker = 'Nature lesson complete: ' + slug
                page.wait_for_function("marker => [...document.querySelectorAll('.jp-Notebook .jp-OutputArea-output')].some(e=>e.textContent.includes(marker))",arg=marker,timeout=180000)
                assert 'Nature lesson complete:' in last.inner_text()
                if slug == '15_nature_data_and_sampling':
                    surfaces=json.loads((ROOT/'content/data/nature-city-surfaces.json').read_text(encoding='utf-8'))['cities']
                    selected=next(c for c in surfaces if c['city']=='Abidjan' and 'DeltaDTM' in c['model'])
                    label=f"{selected['city']} — {selected['model']}"
                    page.locator('.jp-Notebook:visible .widget-dropdown select').select_option(label=label)
                    notice=page.locator('.nature-terrain-view')
                    expect(notice).to_contain_text('PUBLIC TERRAIN: '+selected['city'])
                    expect(notice).to_contain_text(selected['model'])
                    expect(notice).to_contain_text(selected['source_doi'])
                    z=[[v if v is not None and v > -7 else None for v in row] for row in selected['z_msl']]
                    expect_plot_values(page,'nature-terrain-output',[
                        {'type':kind,'x':selected['longitude'],'y':selected['latitude'],'z':z}
                        for kind in ['heatmap','surface']])
                elif slug == '16_facility_comparison':
                    public=json.loads((ROOT/'content/data/nature-aggregates.json').read_text(encoding='utf-8'))
                    selected=next(m for m in public['models'] if 'FABDEM' in m['label'])
                    card=page.locator('.nature-public-card')
                    controls=page.locator('.jp-Notebook:visible .widget-dropdown select')
                    controls.nth(0).select_option(label=selected['label'])
                    for threshold in [10,0]:
                        result=next(r for r in selected['screening'] if r['threshold_m']==threshold)
                        controls.nth(1).select_option(label=f'{threshold} m')
                        expect(card).to_contain_text(selected['label'])
                        expect(card).to_contain_text(f"height ≤ {threshold} m MSL: {result['at_or_below']};")
                        expect(card).to_contain_text(f"available {result['available']}; cohort {result['total']}")
                        expect_plot_values(page,'nature-public-output',[{
                            'type':'bar','x':['At/below threshold','Above threshold','Unavailable'],
                            'y':[result['at_or_below'],result['above'],result['unavailable']]}])
                elif slug == '17_datum_sensitivity':
                    card=page.locator('.nature-sensitivity-card')
                    expect(card).to_contain_text('at/below 4')
                    slider=page.locator('.jp-Notebook:visible .widget-slider').nth(1).locator('.noUi-handle')
                    slider.focus()
                    for _ in range(10): slider.press('ArrowRight')
                    expect(card).to_contain_text('shift +1.0 m')
                    expect(card).to_contain_text('at/below 2')
                    expect(card).to_contain_text('available 8/10')
                    expect_plot_values(page,'nature-sensitivity-output',[
                        {'type':'scatter'},{'type':'scatter','x':[1.0],'y':[2]}])
                    csv=(b'uid,model,msl_m\nSYNTHETIC-SMOKE-A,browser-fixture,0\n'
                         b'SYNTHETIC-SMOKE-B,browser-fixture,0.5\nSYNTHETIC-SMOKE-C,browser-fixture,2\n'
                         b'SYNTHETIC-SMOKE-D,browser-fixture,\nSYNTHETIC-SMOKE-E,browser-fixture,-7\n')
                    # ipywidgets creates a detached file input on button click.
                    # Exercise the user's chooser rather than a nonexistent DOM input.
                    upload=page.get_by_role('button',name='Local sample CSV')
                    with page.expect_file_chooser() as chooser:
                        upload.click()
                    chooser.value.set_files({'name':'synthetic-smoke.csv','mimeType':'text/csv','buffer':csv})
                    expect(page.locator('.jp-Notebook:visible .widget-dropdown select option:checked')).to_have_text('browser-fixture')
                    expect(card).to_contain_text('PRIVATE uploaded samples')
                    expect(card).to_contain_text('at/below 1')
                    expect(card).to_contain_text('available 3/5')
                    expect_plot_values(page,'nature-sensitivity-output',[
                        {'type':'scatter'},{'type':'scatter','x':[1.0],'y':[1]}])
                    # Rejected replacement must not replace the last valid dataframe.
                    bad=b'uid,model,msl_m\nx,rejected,0\n x , rejected ,1\n'
                    with page.expect_file_chooser() as chooser:
                        upload.click()
                    chooser.value.set_files({'name':'invalid-smoke.csv','mimeType':'text/csv','buffer':bad})
                    expect(page.get_by_role('alert')).to_contain_text('Invalid CSV')
                    expect(page.locator('.jp-Notebook:visible .widget-dropdown select option:checked')).to_have_text('browser-fixture')
                    expect(card).to_contain_text('at/below 1')
                    expect(card).to_contain_text('available 3/5')
                    expect_plot_values(page,'nature-sensitivity-output',[
                        {'type':'scatter'},{'type':'scatter','x':[1.0],'y':[1]}])
                    page.get_by_role('button',name='Restore fictional demo',exact=True).click()
                    expect(page.locator('.jp-Notebook:visible .widget-dropdown select option:checked')).to_have_text('fictional')
                    expect(card).to_contain_text('FICTIONAL demo')
                    expect(card).to_contain_text('shift +0.0 m')
                    expect(card).to_contain_text('at/below 4')
                    expect(card).to_contain_text('available 8/10')
                    expect_plot_values(page,'nature-sensitivity-output',[
                        {'type':'scatter'},{'type':'scatter','x':[0.0],'y':[4]}])
            if slug=='00_start_here':
                assert page.locator('.jp-Notebook:visible img[alt^="Conceptual comic:"]').evaluate('(img) => img.complete && img.naturalWidth > 0'), 'Conceptual comic did not load'
                frame=page.frame_locator('.jp-Notebook:visible iframe[title="Fictional coastal facilities dashboard"]')
                expect(frame.locator('#card2')).to_have_text('108',timeout=60000)
            elif slug in ['01_read_the_poster','07_three_dimensions']:
                frame=page.frame_locator('.jp-Notebook:visible iframe[title="Interactive teaching figure"]').first
                expect(frame.locator('.js-plotly-plot')).to_be_attached(timeout=60000)
            elif slug=='05_dashboard_lab':
                expect(page.locator('.jp-Notebook:visible .widget-dropdown').first).to_be_attached(timeout=60000)
                expect(page.locator('.jp-Notebook:visible .jp-OutputArea-output').filter(has_text='Reconciled:')).to_be_attached(timeout=60000)
            elif slug=='09_hotspots':
                expect(page.locator('.jp-Notebook:visible .jp-OutputArea-output').filter(has_text='Monte Carlo p-value for strongest tested window:')).to_be_attached(timeout=60000)
            elif slug=='13_powerbi_in_browser':
                expect(page.locator('.jp-Notebook:visible .jp-OutputArea-output').filter(has_text='Live API lookup disabled.')).to_be_attached(timeout=60000)
                assert not powerbi_requests,'Default run must not contact Power BI'
                address=page.get_by_placeholder('https://app.powerbi.com/groups/.../reports/...')
                configured=json.loads((ROOT/'content/data/powerbi-report.json').read_text(encoding='utf-8'))['report_url']
                expect(address).to_have_value(configured)
                view_button=page.locator('.jp-Notebook:visible .widget-button').filter(has_text='View report')
                address.fill('https://example.org/report')
                view_button.click()
                expect(page.get_by_role('alert')).to_contain_text('app.powerbi.com')
                assert not powerbi_requests
                address.fill(configured)
                page.locator('.jp-Notebook:visible .widget-dropdown select').select_option(label='RESULTS RCP 8.5 (C)')
                view_button.click()
                frame=page.frame_locator('iframe[title="Original AIDS 2024 Power BI report"]')
                expect(frame.get_by_text('Mock Power BI frame for interface test')).to_be_visible(timeout=30000)
                assert parse_qs(urlsplit(powerbi_requests[-1]).query)['pageName']==['ReportSection053da660fb1b33e00c07']
                assert urlsplit(powerbi_requests[-1]).netloc=='app.powerbigov.us'
            assert not page.locator('.jp-OutputArea-error').count(),page.locator('.jp-OutputArea-error').all_text_contents()
            assert not errors,errors
            page.screenshot(path=str(out/(slug+'-lite.png')),full_page=True)
            results.append({'notebook':slug,'status':'pass','seconds':round(time.monotonic()-started,1)})
            print('PASS',slug,flush=True);page.close()
        browser.close()
    (out/'lite-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
if __name__=='__main__':main()
