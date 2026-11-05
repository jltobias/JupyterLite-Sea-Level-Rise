"""Build public terrain teaching views from licensed MSL rasters, never facilities.

These views are sparse nearest-cell samples for illustration, not exposure grids.
The five city anchors are the existing public poster map anchors.
"""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
import argparse, json
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
from analyze_nature import read_manifest, sha256

ROOT = Path(__file__).resolve().parents[1]

def prepare_surfaces(manifest, anchors):
    """Validate MSL inputs and make display grids without any facility records."""
    manifest = Path(manifest)
    models = read_manifest(manifest)
    views, inventory, coverage = [], [], []
    for model in models:
        with ExitStack() as stack:
            paths = [manifest.parent / p for p in model['paths']]
            existing = [p for p in paths if p.is_file()]
            sources=[stack.enter_context(rasterio.open(p)) for p in existing]
            coverage.append(dict(model=model['id'], available_files=len(existing),
                                 missing_files=len(paths)-len(existing),
                                 status='available' if sources else 'unavailable'))
            if not sources:
                continue
            if any(s.crs is None or s.crs.to_epsg()!=4326 for s in sources):
                raise ValueError('Surface preparation requires WGS84 geographic source grids.')
            band = model.get('band', 1)
            if any(band > s.count for s in sources):
                raise ValueError('Raster must contain the requested band.')
            for path, source in zip(existing, sources):
                inventory.append(dict(model=model['id'], filename=path.name,
                    sha256=sha256(path), source_doi=model['source_url'],
                    dataset=model['dataset'], version=model['version'], datum='MSL', unit='m',
                    band=band, scale=source.scales[band-1], offset=source.offsets[band-1],
                    crs=str(source.crs), shape=[source.height, source.width],
                    pixel_size=list(source.res), nodata=str(source.nodata)))

            def copy_decoded_first(merged, new, merged_mask, new_mask, index, **kwargs):
                # Decode each input independently: tiles may have different
                # encodings. NoData allows fallback, but a finite <=-7 value
                # keeps first-source precedence and is masked after merging.
                decoded = np.asarray(new, dtype=float) * sources[index].scales[band-1] + sources[index].offsets[band-1]
                valid = merged_mask & ~new_mask & np.isfinite(decoded)
                np.copyto(merged, decoded, where=valid, casting='unsafe')

            for city,lat,lon in anchors:
                # 0.3 x 0.3 degrees. Coarse GLL retains its native cell size;
                # 30m products are sampled every 0.002 degrees (~220m latitude).
                res=max(.002, max(s.res[0] for s in sources))
                array,transform=merge(sources,bounds=(lon-.15,lat-.15,lon+.15,lat+.15),
                    res=res,resampling=Resampling.nearest,nodata=np.nan,dtype='float32',
                    indexes=[band], method=copy_decoded_first)
                z=array[0].astype(float)
                z[(z<=-7)|~np.isfinite(z)]=np.nan
                h,w=z.shape
                xs=[round(transform.c+(i+.5)*transform.a,6) for i in range(w)]
                ys=[round(transform.f+(j+.5)*transform.e,6) for j in range(h)]
                grid=[[round(float(v),2) if np.isfinite(v) else None for v in row] for row in z]
                views.append(dict(city=city,longitude=xs,latitude=ys,z_msl=grid,
                    model=model['label'],source_doi=model['source_url'],
                    grid_note=f'Nearest-cell display samples on a {res:g} degree grid, 0.3 degree square around a public city anchor. Values rounded to 0.01m for storage, not claimed accuracy. NoData and values <=-7m masked. No facility locations. Not used for facility classification.'))
    return dict(license='CC-BY-NC-SA-4.0',
        attribution='Adapted from Seeger, K. and Minderhoud, P. S. J. (2026), MSL-referenced GLL-DTM v2, FABDEM v1.0 and DeltaDTM v1.1; https://doi.org/10.1038/s41586-026-10196-1. Underlying DEM creators: Vernimmen and Hooijer; Hawker and Neal; Pronk et al. See nature-sources.json for product DOIs.',
        license_url='https://creativecommons.org/licenses/by-nc-sa/4.0/',
        transformation='Cropped at public city anchors; sparse nearest-cell display sampling; -7m and NoData masks; rounding. These are terrain examples, not facility or inundation maps.',
        provenance=dict(generated_utc=datetime.now(timezone.utc).isoformat(),
            manifest_sha256=sha256(manifest), generator='scripts/prepare_nature_surfaces.py',
            generator_sha256=sha256(Path(__file__)),
            software=dict(numpy=np.__version__, rasterio=rasterio.__version__, gdal=rasterio.__gdal_version__),
            source_files=inventory, model_coverage=coverage), cities=views)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    args=ap.parse_args()
    poster=json.loads((ROOT/'content/data/poster-aggregates.json').read_text())
    anchors=sorted({(r['city'],r['latitude'],r['longitude']) for r in poster if r['scope']=='city'})
    output = prepare_surfaces(args.manifest, anchors)
    target=ROOT/'content/data/nature-city-surfaces.json'
    target.write_text(json.dumps(output,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')
    print('Wrote',len(output['cities']),'public terrain views;',target.stat().st_size,'bytes;',sha256(target))

if __name__=='__main__': main()
