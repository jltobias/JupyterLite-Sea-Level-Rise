"""Check built internal HTML links, required assets and source notebook validity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import nbformat,json
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'_site'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in {'src','href','poster'} and v:self.links.append(v)

def main():
    required=['index.html','dashboard/index.html','dashboard/app.js','book/intro.html',
              'book/glossary.html','book/data-dictionary.html','book/references.html',
              'lite/lab/index.html','lite/jupyter-lite.json','assets/plotly.min.js',
              'lite/assets/continuity-comic.png',
              'lite/files/powerbi_bridge.py','data/powerbi-report.json',
              'book/notebooks/13_powerbi_in_browser.html',
              'assets/scenario-walkthrough.mp4','assets/scenario-walkthrough.vtt',
              'data/poster_aggregates.csv','data/synthetic_facilities.csv']
    errors=[f'Missing {p}' for p in required if not (SITE/p).exists()]
    # JupyterLite webpack assets resolve dynamically; validate authored/book HTML links.
    pages=[SITE/'index.html',SITE/'dashboard/index.html',* [p for p in (SITE/'book').rglob('*.html') if not any(part.startswith('_') for part in p.relative_to(SITE/'book').parts)]]
    for page in pages:
        parser=Links();parser.feed(page.read_text(encoding='utf-8'))
        for url in parser.links:
            parsed=urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:continue
            target=(SITE/parsed.path.lstrip('/')) if parsed.path.startswith('/') else page.parent/unquote(parsed.path)
            if not target.exists():errors.append(f'{page.relative_to(SITE)} -> {url}')
    notebooks=sorted((ROOT/'content/notebooks').glob('*.ipynb'))
    lesson_index=json.loads((ROOT/'content/lesson-index.json').read_text(encoding='utf-8'))
    assert {p.stem for p in notebooks}=={lesson['slug'] for lesson in lesson_index}
    for path in notebooks:
        n=nbformat.read(path,as_version=4);nbformat.validate(n)
        lite=nbformat.read(SITE/'lite/files/notebooks'/path.name,as_version=4)
        assert lite.metadata.kernelspec.name=='python',f'Wrong browser kernel: {path.name}'
        for c in n.cells:
            if c.cell_type=='code':
                assert c.execution_count is not None, f'Unexecuted cell: {path.name}'
                assert not any(o.output_type=='error' for o in c.outputs),path.name
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(pages)} authored/book pages, {len(notebooks)} executed notebooks and required assets.')
if __name__=='__main__':main()
