"""Local, authorized facility sampling. Public outputs contain portfolio aggregates only.

Example: python scripts/analyze_nature.py private-data/sites.xlsx \
  --manifest private-data/nature-rasters.json

Raster paths are local and relative to the manifest. No downloads occur. The
manifest is a {"models": [...]} object; see book/source-audit.md for its contract.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
from importlib.metadata import version, PackageNotFoundError
import hashlib
import json
import re
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
from naturelab import THRESHOLDS, screening_summary, paired_comparison, flag_overlap, common_model_comparison

FLAG_FIELDS = {f'{letter}{year % 100:02d}': (scenario, year)
               for letter, scenario in [('A', 'RCP 2.6'), ('B', 'RCP 4.5'), ('C', 'RCP 8.5')]
               for year in range(2030, 2101, 10)}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def private_directory(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / 'private-data').resolve()):
        raise ValueError('Detailed output must be inside this repository\'s ignored private-data/ directory.')
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_workbook(frame, latitude='Latitude', longitude='Longitude'):
    required = {'uid', 'PEPFARSUP', 'ACTUALE', latitude, longitude, *FLAG_FIELDS}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f'Required workbook columns missing: {sorted(missing)}')
    if frame.uid.isna().any() or frame.uid.astype(str).str.strip().eq('').any():
        raise ValueError('Missing uid: every source row must have an identifier.')
    if frame.uid.astype(str).str.strip().duplicated().any():
        raise ValueError('Duplicate uid: resolve source rows explicitly before sampling.')
    if not frame.PEPFARSUP.isin([0, 1]).all():
        raise ValueError('PEPFARSUP must contain only numeric 0 or 1; no implicit support coercion.')
    supported = frame.loc[frame.PEPFARSUP.eq(1)].copy().reset_index(drop=True)
    for field in FLAG_FIELDS:
        if not supported[field].isin(['RED', 'ORANGE', 'YELLOW', 'NOFILL']).all():
            raise ValueError(f'Unknown or missing category in supported rows of {field}.')
    # Missing/invalid coordinates remain in the cohort, with explicit audit flags.
    for field in [latitude, longitude, 'ACTUALE']:
        numeric = pd.to_numeric(supported[field], errors='coerce')
        supported[field] = numeric.where(np.isfinite(numeric), np.nan)
    supported['coordinate_valid'] = (supported[latitude].between(-90, 90)
                                     & supported[longitude].between(-180, 180))
    return supported


def audit_baseline(frame):
    poster = pd.read_csv(ROOT / 'content/data/poster_aggregates.csv')
    expected = {(r.scenario, int(r.year)): int(r.potentially_flooded)
                for r in poster[poster.scope.eq('portfolio')].itertuples()}
    rows = []
    for field, (scenario, year) in FLAG_FIELDS.items():
        count = int(frame[field].isin(['RED', 'ORANGE', 'YELLOW']).sum())
        rows.append({'scenario': scenario, 'year': year, 'source_field': field,
                     'observed': count, 'poster': expected[(scenario, year)],
                     'matches': count == expected[(scenario, year)]})
    return {'supported_denominator': len(frame), 'poster_denominator': 25873,
            'denominator_matches': len(frame) == 25873,
            'all_24_match': all(row['matches'] for row in rows), 'counts': rows}


def original_elevation_audit(frame):
    values = frame.ACTUALE.to_numpy(dtype=float)
    return {'total': len(values), 'finite': int(np.isfinite(values).sum()),
            'missing_or_invalid': int((~np.isfinite(values)).sum()),
            'zero': int((values == 0).sum()),
            'le_minus7': int((np.isfinite(values) & (values <= -7)).sum()),
            'interpretation': 'Raw original ACTUALE, modeled as ACTUAL_MHHW_ELEV_M. Numeric availability is not verified elevation validity. Zeros may encode unassessed/fill values; retain them for audit, do not assume valid zero elevation.'}


def read_manifest(path):
    manifest = json.loads(Path(path).read_text(encoding='utf-8'))
    models = manifest.get('models')
    if not isinstance(models, list) or not models:
        raise ValueError('Manifest requires a nonempty models list.')
    seen = set()
    for model in models:
        if not isinstance(model, dict):
            raise ValueError('Every manifest model must be an object.')
        for field in ['id', 'label', 'dataset', 'version', 'datum', 'license', 'source_url', 'paths']:
            if field not in model:
                raise ValueError(f'Manifest model missing {field}.')
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', str(model['id'])) or model['id'] in seen:
            raise ValueError('Model ids must be unique letters/digits/underscores/hyphens.')
        seen.add(model['id'])
        if model['datum'] != 'MSL' or model.get('unit', 'm') != 'm':
            raise ValueError('Sampler accepts already-corrected MSL rasters in metres only. Do not apply MDT again.')
        if not isinstance(model['paths'], list) or not all(isinstance(p, str) for p in model['paths']):
            raise ValueError('Model paths must be a list of local filenames (an empty list means unavailable).')
        if any('://' in p for p in model['paths']):
            raise ValueError('Download source rasters locally first; remote raster URLs are not opened.')
        if not isinstance(model.get('band', 1), int) or model.get('band', 1) < 1:
            raise ValueError('Raster band must be a positive integer.')
    return models


def sample_model(frame, model, manifest_directory, latitude='Latitude', longitude='Longitude'):
    """Sample the containing pixel (nearest grid cell; no interpolation).

    WGS84 longitude/latitude are transformed to each raster CRS in x/y order.
    First finite unmasked value in manifest path order wins in overlaps; NoData
    permits fallback to another tile. Bounds use rasterio row/column indexing
    (upper/left inclusive, lower/right exclusive). Apply band scale/offset.
    Values <= -7 are retained privately and excluded, never rescued by another
    tile. No reprojection of rasters, bilinear interpolation or extrapolation.
    """
    values = np.full(len(frame), np.nan)
    coords_ok = frame.coordinate_valid.to_numpy()
    statuses = np.where(coords_ok, 'missing_raster', 'invalid_coordinate').astype(object)
    sources = []
    paths = [Path(manifest_directory) / p for p in model['paths']]
    existing = [p for p in paths if p.is_file()]
    statuses[coords_ok] = 'outside_coverage' if existing else 'missing_raster'
    if existing:
        import rasterio
        from rasterio.warp import transform
        for path in existing:
            with rasterio.open(path) as raster:
                band = model.get('band', 1)
                if raster.crs is None or band > raster.count:
                    raise ValueError('Raster must have a declared CRS and the requested band.')
                sources.append({'path': str(path.resolve()), 'sha256': sha256(path),
                                'crs': str(raster.crs), 'shape': [raster.height, raster.width],
                                'pixel_size': list(raster.res), 'nodata': str(raster.nodata),
                                'scale': raster.scales[band - 1], 'offset': raster.offsets[band - 1]})
                use = np.flatnonzero(coords_ok & ~np.isfinite(values))
                if not len(use):
                    continue
                lon = frame.loc[use, longitude].tolist()
                lat = frame.loc[use, latitude].tolist()
                try:
                    xx, yy = transform('EPSG:4326', raster.crs, lon, lat)
                except Exception:
                    # GDAL versions expose different low-level transform errors.
                    # Isolate failed points so one out-of-domain coordinate does
                    # not discard valid rows in the same regional CRS batch.
                    xx, yy = np.full(len(use), np.nan), np.full(len(use), np.nan)
                    for position, (x, y) in enumerate(zip(lon, lat)):
                        try:
                            tx, ty = transform('EPSG:4326', raster.crs, [x], [y])
                            xx[position], yy[position] = tx[0], ty[0]
                        except Exception:
                            pass  # Nonfinite entries become invalid_transform below.
                finite = np.isfinite(xx) & np.isfinite(yy)
                statuses[use[~finite]] = 'invalid_transform'
                usable = use[finite]
                points = np.column_stack([np.asarray(xx)[finite], np.asarray(yy)[finite]])
                for idx, point in zip(usable, points):
                    row, col = raster.index(*point)
                    if row < 0 or row >= raster.height or col < 0 or col >= raster.width:
                        continue
                    cell = next(raster.sample([point], indexes=band, masked=True))
                    if np.ma.getmaskarray(cell)[0] or not np.isfinite(cell[0]):
                        statuses[idx] = 'nodata'
                        continue
                    value = float(cell[0]) * raster.scales[band - 1] + raster.offsets[band - 1]
                    if not np.isfinite(value):
                        statuses[idx] = 'nodata'
                        continue
                    values[idx] = value
                    statuses[idx] = 'excluded_le_minus7' if value <= -7 else 'available'
    return values, statuses, sources, len(paths) - len(existing)


def analyze(workbook, manifest, private_output=None, public_output=None, sheet='Climate-Sites-w-coords',
            latitude='Latitude', longitude='Longitude'):
    private_output = private_directory(private_output or ROOT / 'private-data/nature')
    public_output = Path(public_output or ROOT / 'content/data')
    models = read_manifest(manifest)
    # Read only required fields; clinical indicators/names never enter this pipeline.
    required = {'uid', 'PEPFARSUP', 'ACTUALE', latitude, longitude, *FLAG_FIELDS}
    frame = pd.read_excel(workbook, sheet_name=sheet, dtype={'uid': str},
                          usecols=lambda name: name in required, engine='openpyxl')
    frame = validate_workbook(frame, latitude, longitude)
    generated = datetime.now(timezone.utc).isoformat()
    software = {}
    for package in ['numpy', 'pandas', 'openpyxl', 'rasterio']:
        try:
            software[package] = version(package)
        except PackageNotFoundError:
            software[package] = 'not installed; no raster sampled'
    result = {'schema_version': 1, 'generated_at': generated, 'status': 'source-unavailable',
              'software': software,
              'scope': 'supported portfolio only', 'cohort': 'PEPFARSUP = 1; unique uid rows',
              'workbook_sha256': sha256(workbook), 'baseline_audit': audit_baseline(frame),
              'original_elevation_audit': original_elevation_audit(frame),
              'coordinate_audit': {'valid': int(frame.coordinate_valid.sum()),
                                   'invalid': int((~frame.coordinate_valid).sum())},
              'license': 'CC-BY-NC-SA-4.0 for derived corrected-raster aggregates',
              'limitations': [
                  'Static <=0, <=1 and <=10 m MSL thresholds are not RCP/year forecasts, flood probabilities, inundation extents or clinical impacts.',
                  'Original ACTUALE is modeled as ACTUAL_MHHW_ELEV_M; do not apply a geoid/MDT correction to it blindly.',
                  'Original numeric heights are unverified: zeros may be unassessed/fill values. Numeric pairs are optional raw audits, not validated elevation comparisons.',
                  'New DEM versus original differences combine terrain, datum, epoch and resolution, not datum alone.',
                  'MSL raster cells <=-7 m are excluded; missing/out-of-coverage cells remain unavailable.',
                  'GLL-DTMv2 approximately 1 km cells support portfolio screening, not site design.',
                  'RCP colour categories are flags; overlap tables are not validation against ground truth.'],
              'sampling': {'method': 'containing pixel / nearest grid cell; no interpolation',
                           'input_crs': 'EPSG:4326; longitude then latitude',
                           'overlap': 'first finite unmasked cell in manifest path order',
                           'nodata': 'mask/nonfinite -> unavailable; try later overlapping tiles',
                           'datum': 'already MSL; no second correction',
                           'scale_offset': 'raster band scale and offset applied'}, 'models': []}
    private_sources, samples, summaries, model_heights = {}, [], [], {}
    for model in models:
        raw, statuses, sources, missing = sample_model(frame, model, Path(manifest).resolve().parent,
                                                      latitude, longitude)
        model_heights[model['id']] = raw
        available = int((statuses == 'available').sum())
        status = 'available' if available == len(frame) and len(frame) else 'partial' if available else 'source-unavailable'
        record = {k: model[k] for k in ['id', 'label', 'dataset', 'version', 'datum', 'license', 'source_url']}
        for key in ['upstream_sha256', 'source_sha256', 'processing_note', 'coverage_note']:
            if key in model:
                record[key] = model[key]
        record.update(status=status, missing_raster_files=missing,
                      raster_sha256=[s['sha256'] for s in sources],
                      coverage={str(k): int(v) for k, v in pd.Series(statuses).value_counts().items()},
                      screening=[screening_summary(raw, t) for t in THRESHOLDS],
                      paired_original=[paired_comparison(frame.ACTUALE.to_numpy(), raw, t) for t in THRESHOLDS],
                      rcp_overlap=[{'scenario': scenario, 'year': year, 'threshold_m': t,
                                    **flag_overlap(frame[field].to_numpy(), raw, t)}
                                   for field, (scenario, year) in FLAG_FIELDS.items() for t in THRESHOLDS])
        result['models'].append(record)
        private_sources[model['id']] = sources
        samples.append(pd.DataFrame({'uid': frame.uid, 'model': model['id'],
                                     'msl_m': raw, 'sample_status': statuses,
                                     'original_mhhw_m': frame.ACTUALE,
                                     'latitude': frame[latitude], 'longitude': frame[longitude]}))
        summaries.extend({'model': model['id'], 'status': status, **s} for s in record['screening'])
    result['common_cohort'] = [common_model_comparison(model_heights, t) for t in THRESHOLDS]
    if all(m['status'] == 'available' for m in result['models']):
        result['status'] = 'available'
    elif any(m['status'] != 'source-unavailable' for m in result['models']):
        result['status'] = 'partial'
    # The only detailed records and filesystem paths are written under private-data.
    pd.concat(samples, ignore_index=True).to_csv(private_output / 'samples.csv', index=False)
    frame.to_csv(private_output / 'workbook-audit.csv', index=False)
    (private_output / 'sampling-provenance.json').write_text(json.dumps({
        'generated_at': generated, 'workbook_sha256': result['workbook_sha256'],
        'manifest_sha256': sha256(manifest), 'sources': private_sources}, indent=2) + '\n', encoding='utf-8')
    public_output.mkdir(parents=True, exist_ok=True)
    (public_output / 'nature-aggregates.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    pd.DataFrame(summaries).to_csv(public_output / 'nature-summary.csv', index=False)
    source_manifest = public_output / 'nature-sources.json'
    if source_manifest.is_file():
        catalog = json.loads(source_manifest.read_text(encoding='utf-8'))
        for product in catalog['products']:
            sampled = next((m for m in result['models'] if m['source_url'] == product['source_url']), None)
            product['use_status'] = 'used' if sampled and sampled['raster_sha256'] else 'planned'
        source_manifest.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workbook', type=Path)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--private-output', type=Path, default=ROOT / 'private-data/nature')
    ap.add_argument('--public-output', type=Path, default=ROOT / 'content/data')
    ap.add_argument('--sheet', default='Climate-Sites-w-coords')
    ap.add_argument('--latitude-column', default='Latitude')
    ap.add_argument('--longitude-column', default='Longitude')
    args = ap.parse_args()
    result = analyze(args.workbook, args.manifest, args.private_output, args.public_output, args.sheet,
                     args.latitude_column, args.longitude_column)
    print('Nature aggregate status:', result['status'])
    print('All 24 original poster counts match:', result['baseline_audit']['all_24_match'])
    print('Original denominator matches:', result['baseline_audit']['denominator_matches'])
    print('Detailed records written only under private-data; public files contain portfolio aggregates.')
    if not result['baseline_audit']['all_24_match'] or not result['baseline_audit']['denominator_matches']:
        print('DISCREPANCY: inspect the aggregate baseline_audit before interpreting comparisons.')


if __name__ == '__main__':
    main()
