"""Run representative real notebooks in a headless browser's Pyodide kernel."""
from pathlib import Path
import argparse,json,time
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8000');args=ap.parse_args()
    out=ROOT/'tmp/browser';out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        context=browser.new_context(viewport={'width':1400,'height':1000})
        for slug in ['00_start_here','01_read_the_poster','05_dashboard_lab','07_three_dimensions','09_hotspots']:
            print('RUN',slug,flush=True)
            started=time.monotonic();page=context.new_page();errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(args.url+f'/lite/lab/index.html?path=notebooks/{slug}.ipynb',wait_until='networkidle')
            page.get_by_role('tab',name=slug+'.ipynb',exact=True).click(timeout=60000)
            page.wait_for_selector('.jp-Notebook:visible',timeout=60000)
            # Wait for Pyodide before sending execution requests. Clicking Run during
            # session creation can race the kernel chooser and discard that request.
            page.wait_for_function("() => document.querySelector('[role=dialog]') || [...document.querySelectorAll('.jp-KernelStatus-success')].some(e=>e.offsetParent!==null)",timeout=180000)
            if page.get_by_role('dialog').count():
                page.get_by_role('button',name='Select',exact=True).click()
            page.wait_for_selector('.jp-KernelStatus-success:visible',timeout=180000)
            page.get_by_role('menuitem',name='Run',exact=True).click();page.get_by_role('menuitem',name='Run All Cells',exact=True).click()
            page.wait_for_function("() => [...[...document.querySelectorAll('.jp-Notebook')].find(n=>n.offsetParent!==null).querySelectorAll('.jp-OutputArea-output')].some(e=>e.textContent.includes('Ready: public poster'))",timeout=180000)
            # Notebook virtualization is disabled in overrides.json; reveal the final cell.
            last=page.locator('.jp-Notebook:visible .jp-Cell').last
            last.scroll_into_view_if_needed()
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
            else:
                expect(page.locator('.jp-Notebook:visible .jp-OutputArea-output').filter(has_text='Monte Carlo p-value for strongest tested window:')).to_be_attached(timeout=60000)
            assert not page.locator('.jp-OutputArea-error').count(),page.locator('.jp-OutputArea-error').all_text_contents()
            assert not errors,errors
            page.screenshot(path=str(out/(slug+'-lite.png')),full_page=True)
            results.append({'notebook':slug,'status':'pass','seconds':round(time.monotonic()-started,1)})
            print('PASS',slug,flush=True);page.close()
        browser.close()
    (out/'lite-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
if __name__=='__main__':main()
