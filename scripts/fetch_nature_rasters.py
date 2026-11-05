"""Download only the pinned public Nature rasters; no facility inputs are read.

The source host uses port 9443. If unavailable locally, the manually triggered
fetch-nature-sources GitHub workflow runs this same command. About 4 GB is
transferred before lossless compression (approximately 600 MB retained).
"""
from pathlib import Path
from urllib.parse import urlparse
import argparse
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def download(url, destination):
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname!='data.yoda.wur.nl':
        raise ValueError('Only pinned HTTPS public WUR source URLs are accepted.')
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={'X-Requested-With':'XMLHttpRequest'})
            with urllib.request.urlopen(request,timeout=90) as response, destination.open('wb') as target:
                while block:=response.read(4*1024*1024): target.write(block)
            return
        except (OSError,TimeoutError):
            if attempt==2: raise
            time.sleep(2*(attempt+1))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'private-data/nature-download')
    args=ap.parse_args()
    output=args.output.resolve()
    if not output.is_relative_to((ROOT/'private-data').resolve()):
        raise ValueError('Use a directory under this repository\'s ignored private-data/.')
    import rasterio.shutil
    catalog=json.loads((ROOT/'content/data/nature-raster-catalog.json').read_text())
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    groups={}
    for item in catalog['files']:
        target=(output/item['filename']).resolve()
        if not target.is_relative_to(output): raise ValueError('Unsafe catalog filename.')
        target.parent.mkdir(parents=True,exist_ok=True)
        raw=target.with_suffix('.source.part')
        download(item['url'],raw)
        source_hash=digest(raw)
        if source_hash!=item['source_sha256']:
            raise ValueError('Source changed: SHA256 mismatch for '+item['filename'])
        rasterio.shutil.copy(raw,target,driver='COG',COMPRESS='DEFLATE',BIGTIFF='IF_SAFER',OVERVIEWS='NONE')
        raw.unlink()  # Only this download's verified temporary file.
        records.append({**item,'downloaded_source_sha256':source_hash,'local_sha256':digest(target)})
        groups.setdefault(item['model'],[]).append(item)
        print('Verified source and compressed:',item['filename'],flush=True)
    labels={'gll':'GLL-DTM v2','fabdem':'FABDEM v1.0','deltadtm':'DeltaDTM v1.1'}
    versions={'gll':'2','fabdem':'1.0','deltadtm':'1.1'}
    models=[]
    for model,items in groups.items():
        base=items[0]['url'].split('/original/')[0]
        download(base+'/License.txt',output/(model+'-LICENSE.txt'))
        download(base+'/original/README.txt',output/(model+'-README.txt'))
        regional=model!='gll'
        models.append(dict(id=model+'-msl',label=labels[model]+(' (five poster-city regions)' if regional else ' (global coastal lowlands)'),
            dataset=labels[model]+' referenced to MSL (MDT HYBRID-CNES-CLS2022)',version=versions[model],datum='MSL',unit='m',
            source_url='https://doi.org/'+items[0]['doi'],license='CC-BY-NC-SA-4.0',paths=[i['filename'] for i in items],band=1,
            coverage_note=catalog['selection']+'; entire selected tiles sampled.' if regional else 'Global source coverage; NoData retained. Approximately 1km grid.',
            processing_note='Verified original SHA256 against pinned catalog; lossless COG compression; already MSL, no second datum correction.'))
    (output/'manifest.json').write_text(json.dumps({'models':models},indent=2)+'\n')
    (output/'download-provenance.json').write_text(json.dumps({'license':catalog['license'],'attribution':catalog['authors'],
        'paper':catalog['paper'],'files':records},indent=2)+'\n')
    print('Ready for analyze_nature.py --manifest',output/'manifest.json')

if __name__=='__main__': main()
