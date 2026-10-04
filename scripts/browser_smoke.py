"""Browser integration checks against a running static site; optional Playwright."""
import argparse,csv,io,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8000');args=ap.parse_args()
    out=ROOT/'tmp/browser';out.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(args.url+'/dashboard/',wait_until='networkidle')
        expect(page.locator('#card1')).to_have_text('25,873');expect(page.locator('#card2')).to_have_text('108')
        for scenario,total in [('RCP 2.6','108'),('RCP 4.5','107'),('RCP 8.5','108')]:
            page.get_by_role('button',name=scenario,exact=True).click();expect(page.locator('#card2')).to_have_text(total)
        page.locator('#year').fill('2100');page.locator('#year').dispatch_event('input')
        expect(page.locator('#card2')).to_have_text('412')
        page.locator('#scope').select_option('city');page.locator('#country').select_option('Thailand');page.locator('#city').select_option('Bangkok')
        expect(page.locator('#card1')).to_have_text('19');expect(page.locator('#card2')).to_have_text('16')
        with page.expect_download() as info:page.locator('#download').click()
        download=info.value;download.save_as(out/'selected.csv')
        exported=list(csv.DictReader((out/'selected.csv').open(encoding='utf-8')))
        assert len(exported)==1 and exported[0]['potentially_flooded']=='16' and exported[0]['scenario']=='RCP 8.5'
        page.locator('#scope').select_option('portfolio');expect(page.locator('#card2')).to_have_text('412');expect(page.locator('#country')).to_have_value('All')
        page.locator('#reset').click();page.screenshot(path=str(out/'dashboard-desktop.png'),full_page=True)
        for view in ['bars','cube','map']:
            page.locator(f'[data-view="{view}"]').click()
            page.wait_for_function("() => !!document.querySelector('#visual')._fullLayout")
        page.locator('#dataset').select_option('synthetic');page.locator('#country').select_option('Thailand');page.locator('#city').select_option('Bangkok');page.locator('#supported').check()
        expect(page.locator('#card1')).to_have_text('18')
        before=int(page.locator('#card2').inner_text());page.locator('#threshold').fill('80');page.locator('#threshold').dispatch_event('input')
        assert int(page.locator('#card2').inner_text())<=before
        expect(page.locator('#card1')).to_have_text('18')
        page.locator('#search').fill('NO-SUCH-ID');expect(page.locator('#tableCount')).to_contain_text('0 of 18');expect(page.locator('#card1')).to_have_text('18')
        page.locator('[data-view="terrain"]').click();page.wait_for_function("() => document.querySelector('#visual').data?.[0]?.type === 'surface'")
        page.screenshot(path=str(out/'terrain.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});page.locator('#dataset').select_option('poster');page.locator('#reset').click()
        page.wait_for_function('document.documentElement.scrollWidth <= innerWidth+2')
        page.wait_for_function("['visual','series','composition'].every(id=>{const e=document.getElementById(id);return e._fullLayout.width<=e.clientWidth+2;})")
        page.screenshot(path=str(out/'dashboard-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000});page.goto(args.url+'/',wait_until='networkidle');page.screenshot(path=str(out/'landing.png'),full_page=True)
        page.goto(args.url+'/book/notebooks/01_read_the_poster.html',wait_until='networkidle')
        figure=page.frame_locator('iframe[title="Interactive teaching figure"]').first
        expect(figure.locator('.js-plotly-plot')).to_be_visible()
        page.screenshot(path=str(out/'book.png'),full_page=True)
        browser.close()
    assert not errors,errors
    print('PASS: browser totals, filters, CSV export, synthetic cohort, 3D modes, responsive layout and book Plotly iframe.')
if __name__=='__main__':main()
