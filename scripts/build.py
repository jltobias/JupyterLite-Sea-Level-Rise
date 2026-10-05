"""Execute notebooks and build a single static site: book + JupyterLite + dashboard."""
from pathlib import Path
import argparse, sys, shutil, subprocess, json, os
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    print('+',' '.join(str(x) for x in args),flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--skip-execute',action='store_true');parser.add_argument('--book-only',action='store_true');args=parser.parse_args()
    site=ROOT/'_site';site.mkdir(exist_ok=True)
    if not args.skip_execute:
        for path in sorted((ROOT/'content/notebooks').glob('*.ipynb')):
            print('Executing',path.name,flush=True)
            notebook=nbformat.read(path,as_version=4)
            NotebookClient(notebook,timeout=240,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}}).execute()
            nbformat.write(notebook,path)
    for part in ['notebooks','data','assets']:
        shutil.copytree(ROOT/'content'/part,ROOT/'book'/part,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','my_public_briefing.csv'))
    for module in (ROOT/'content').glob('*.py'):
        shutil.copy2(module,ROOT/'book'/module.name)
    run(sys.executable,'-c','from jupyter_book.cli.main import main; main()','build','book','--warningiserror','--keep-going')
    shutil.copytree(ROOT/'book/_build/html',site/'book',dirs_exist_ok=True)
    shutil.copytree(ROOT/'dashboard',site/'dashboard',dirs_exist_ok=True)
    shutil.copytree(ROOT/'content/data',site/'data',dirs_exist_ok=True)
    shutil.copytree(ROOT/'content/assets',site/'assets',dirs_exist_ok=True)
    shutil.copy2(ROOT/'index.html',site/'index.html')
    (site/'.nojekyll').write_text('',encoding='utf-8')
    if not args.book_only:
        # Strip saved outputs in the Lite copy; the book keeps executed rich examples.
        lite=ROOT/'tmp/lite-content'
        shutil.copytree(ROOT/'content',lite,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','my_public_briefing.csv'))
        for path in (lite/'notebooks').glob('*.ipynb'):
            n=nbformat.read(path,as_version=4)
            for c in n.cells:
                if c.cell_type=='code':c.outputs=[];c.execution_count=None
            n.metadata.pop('widgets',None)
            # Desktop execution uses python3; Lite's installed kernel is named python.
            n.metadata.kernelspec={'name':'python','display_name':'Python (Pyodide)','language':'python'}
            nbformat.write(n,path)
        run(sys.executable,'-c','from jupyterlite_core.app import main; main()','build','--contents',lite,'--output-dir',site/'lite')
        # Markdown can render before Lite's virtual-file service worker is ready.
        # Its ../assets URLs resolve from /lite/lab/, so provide that static route too.
        shutil.copytree(ROOT/'content/assets',site/'lite/assets',dirs_exist_ok=True)
        run(sys.executable,'-c','from jupyterlite_core.app import main; main()','check','--output-dir',site/'lite')
    print('Static site ready:',site,flush=True)

if __name__=='__main__':main()
