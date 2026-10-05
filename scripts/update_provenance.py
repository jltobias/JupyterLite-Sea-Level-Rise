"""Recalculate public artifact hashes; never reads private source workbooks."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    # Match repository LF normalization so hashes survive Windows/Linux checkouts.
    for directory in ['content/data','content/assets']:
        for p in (ROOT/directory).iterdir():
            if p.is_file() and p.suffix in {'.csv','.json','.js','.svg','.css','.vtt'}:
                p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
    sources=[
      {'id':'poster','url':'https://plus.iasociety.org/sites/default/files/2024-09/e-poster_755.pdf',
       'citation':'Tobias et al. (2024), AIDS 2024, poster THPEF698, Tables 1–3',
       'transformation':'Manual count transcription; percentages recomputed; city anchors manually specified; narrative ratios kept separately.',
       'rights':'Composite poster rights retained; no open license verified. Public facts cited, not a license grant over poster artwork.'},
      {'id':'ipcc-ar5','url':'https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_SPM_FINAL.pdf',
       'citation':'IPCC (2013), AR5 WGI Summary for Policymakers, Table SPM.2, p.23',
       'transformation':'Six sea-level reference rows transcribed; global mean; 1986–2005 baseline; period averages.',
       'rights':'IPCC copyright retained; numerical facts cited; report/figure reuse governed by IPCC policy.'},
      {'id':'natural-earth','url':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_land.geojson',
       'citation':'Natural Earth contributors, v5.1.2, 1:110m land',
       'transformation':'Unmodified GeoJSON; geometry only used in charts; not used for exposure classification.',
       'rights':'Public domain; voluntary attribution: Made with Natural Earth.'},
      {'id':'powerbi-page-metadata','url':'https://github.com/jltobias/JupyterLite-Sea-Level-Rise/blob/main/content/data/powerbi-report.json',
       'citation':'User-supplied Prototype-July-8-2024.pbix, Report/Layout, inspected 2026-10-05',
       'transformation':'Only 18 page names, captions and order extracted. No report data, coordinates or credentials; service URL remains unconfigured.',
       'rights':'Original report rights retained; descriptive metadata for the requested integration; no report-data redistribution grant.'},
      {'id':'synthetic','url':'https://github.com/jltobias/JupyterLite-Sea-Level-Rise/blob/main/scripts/generate_data.py',
       'citation':'Coastal Futures teaching fixtures, seed 20240722, version 1.0.0',
       'transformation':'Independent deterministic generation; no original facility rows or coordinates read.',
       'rights':'CC0-1.0 to extent applicable rights held.'}
    ]
    files={}
    for directory in ['content/data','content/assets']:
        for p in sorted((ROOT/directory).iterdir()):
            if p.is_file() and p.name!='provenance.json':files[p.relative_to(ROOT).as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
    result={'version':'1.1.0','inspected_date':'2026-10-05','sources':sources,'files':files,
       'evidence_boundary':'Published poster aggregates, explicit reference facts, and separate fictional labs. No private facility data or proprietary hazard grids distributed.',
       'known_discrepancies':['RCP 2.6 narrative 2.8× versus table 321/108=2.9722…','Percentages recalculated from source counts','Original source field-name/typing anomalies documented without silent correction'],
       'runtime_note':'Desktop build dependencies recorded in build-environment.txt; browser Pyodide packages may differ and require network access on first launch.'}
    original=ROOT/'tmp/poster-source.pdf'
    if original.exists():result['official_poster_sha256']=sha(original)
    (ROOT/'content/data/provenance.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('Hashed',len(files),'public files.')
if __name__=='__main__':main()
