"""Scientific edge cases and privacy boundary of the independent Nature sampler."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
sys.path.insert(0, str(ROOT / 'scripts'))
from naturelab import (msl_elevation, screening_summary, paired_comparison,
                       flag_overlap, read_sample_csv, fictional_samples, coverage_frame, common_model_comparison)
import analyze_nature as sampler


def test_datum_sign_and_missingness():
    assert msl_elevation(1.8, 30.4, 30, .8) == pytest.approx(1.4)
    np.testing.assert_allclose(msl_elevation([2, 2], 31, 30, [.5, 1.5]), [2.5, 1.5])
    assert np.isnan(msl_elevation(np.nan, 0, 0, 0))


def test_equality_exclusions_and_coverage_conservation():
    heights = [-8, -7, -6.9, 0, 1, 10, 10.1, np.nan, np.inf]
    for t, count in [(0, 2), (1, 3), (10, 4)]:
        s = screening_summary(heights, t)
        assert s['at_or_below'] == count
        assert s['available'] == 5 and s['unavailable'] == 4
        assert s['missing'] == 2 and s['excluded_le_minus7'] == 2
        assert s['available'] + s['unavailable'] == s['total']
    assert screening_summary([np.nan, -7], 10)['at_or_below'] is None
    assert screening_summary([], 0)['percent_of_available'] is None
    assert screening_summary(heights, 1, 100)['available'] == 5
    with pytest.raises(ValueError):
        screening_summary(heights, np.nan)


def test_pairing_matrix_conserves_matching_cohort():
    old = [0]*3 + [2]*7 + [np.nan, 0, 0]
    new = [0] + [2]*2 + [0]*3 + [2]*4 + [0, np.nan, -7]
    matrix = paired_comparison(old, new)
    assert matrix['matched'] == 10 and matrix['unmatched'] == 3
    assert matrix['cells'] == {'both_at_or_below': 1, 'original_only': 2, 'nature_only': 3, 'neither': 4}
    assert sum(matrix['cells'].values()) == matrix['matched']
    assert paired_comparison([np.nan], [0])['cells']['neither'] is None
    with pytest.raises(ValueError):
        paired_comparison([1, 2], [1])


def test_flags_are_overlap_not_validation_labels():
    result = flag_overlap(['RED'] + ['ORANGE']*2 + ['NOFILL']*7 + ['YELLOW'],
                          [0] + [2]*2 + [0]*3 + [2]*4 + [np.nan])
    assert result['cells'] == {'flag_and_low': 1, 'flag_only': 2, 'low_only': 3, 'neither': 4}
    assert result['matched'] == 10 and result['unmatched'] == 1
    with pytest.raises(ValueError, match='category'):
        flag_overlap(['purple'], [1])
    for threshold in [np.nan, np.inf, -np.inf]:
        with pytest.raises(ValueError, match='finite'):
            flag_overlap(['RED'], [1], threshold)


def test_common_model_intersection_missingness_and_equality():
    result = common_model_comparison({'a': [0, 1, np.nan, 2, -7], 'b': [2, 1, 0, np.nan, 0]}, 1)
    assert result['matched'] == 2 and result['unmatched'] == 3 and result['total'] == 5
    assert result['counts'] == {'a': 2, 'b': 1}
    assert common_model_comparison({'a': [np.nan], 'b': [0]})['counts'] == {'a': None, 'b': None}
    with pytest.raises(ValueError, match='identical'):
        common_model_comparison({'a': [1, 2], 'b': [1]})


def test_upload_contract_and_controls_use_fixed_coverage():
    csv = b'uid,model,msl_m,latitude\nfictional-1,demo,0,99\nfictional-2,demo,,99\n'
    frame = read_sample_csv(csv)
    assert 'latitude' not in frame.columns and len(frame) == 2
    with pytest.raises(ValueError, match='Duplicate'):
        read_sample_csv(b'uid,model,msl_m\nx,demo,0\nx,demo,1\n')
    with pytest.raises(ValueError, match='Duplicate'):
        read_sample_csv(b'uid,model,msl_m\nx,demo,0\n x , demo ,1\n')
    normalized = read_sample_csv(b'uid,model,msl_m\n x , demo ,1\n')
    assert normalized.loc[0, 'uid'] == 'x' and normalized.loc[0, 'model'] == 'demo'
    demo = fictional_samples()
    assert screening_summary(demo.msl_m, 1, 0)['at_or_below'] == 4
    assert screening_summary(demo.msl_m, 1, 1)['at_or_below'] == 2
    assert screening_summary(demo.msl_m, 10)['at_or_below'] == 7


def test_upload_bytes_cleared_after_valid_invalid_and_restore(monkeypatch):
    import datetime
    import ipywidgets as widgets
    import IPython.display
    import coastlab
    from naturelab import sensitivity_controls
    figures = []
    monkeypatch.setattr(coastlab, 'show', figures.append)
    monkeypatch.setattr(IPython.display, 'display', lambda *_: None)
    ui = sensitivity_controls(allow_upload=True)
    controls = ui.controls
    upload = controls['upload']
    raw = b'uid,model,msl_m\nPRIVATE-SENTINEL-1,uploaded,0\nPRIVATE-SENTINEL-2,uploaded,4\nPRIVATE-SENTINEL-3,uploaded,\n'

    def send(data):
        upload.value = ({'name': 'local.csv', 'type': 'text/csv', 'size': len(data),
                         'last_modified': datetime.datetime.now(datetime.timezone.utc),
                         'content': memoryview(data)},)

    def assert_cleared():
        assert upload.value == ()
        assert upload.get_state()['value'] == []
        saved = json.dumps(widgets.Widget.get_manager_state(widgets=[upload]))
        assert 'content' not in saved and 'PRIVATE-SENTINEL' not in saved

    send(raw)
    assert_cleared()
    assert controls['model'].value == 'uploaded'
    assert 'at/below 1' in controls['card'].value and 'available 2/3' in controls['card'].value
    assert list(figures[-1].data[1].y) == [1]
    send(b'uid,model,msl_m\nPRIVATE-SENTINEL-X,uploaded,not-a-number\n')
    assert_cleared()
    assert 'Invalid CSV' in controls['notice'].value
    assert controls['model'].value == 'uploaded' and 'at/below 1' in controls['card'].value
    controls['offset'].value = 1
    controls['reset'].click()
    assert_cleared()
    assert controls['model'].value == 'fictional' and controls['offset'].value == 0
    assert 'at/below 4' in controls['card'].value and 'available 8/10' in controls['card'].value
    assert list(figures[-1].data[1].y) == [4]


def workbook_frame():
    frame = pd.DataFrame({'uid': ['fixture-a', 'fixture-b', 'fixture-c', 'fixture-d'],
                          'PEPFARSUP': [1, 1, 1, 0], 'ACTUALE': [1, 2, np.nan, 1],
                          'Latitude': [.5, .5, 999, .5], 'Longitude': [.5, 1.5, .5, .5]})
    for field in sampler.FLAG_FIELDS:
        frame[field] = ['RED', 'NOFILL', 'YELLOW', 'NOFILL']
    return frame


def test_workbook_validation_and_baseline_discrepancy():
    f = workbook_frame()
    selected = sampler.validate_workbook(f)
    assert len(selected) == 3
    assert selected.coordinate_valid.tolist() == [True, True, False]
    audit = sampler.audit_baseline(selected)
    assert len(audit['counts']) == 24
    assert not audit['all_24_match'] and not audit['denominator_matches']
    assert all(row['observed'] == 2 for row in audit['counts'])
    for column, value, message in [('uid', 'fixture-a', 'Duplicate'),
                                   ('PEPFARSUP', 2, 'PEPFARSUP'), ('A30', 'PURPLE', 'category')]:
        bad = f.copy()
        bad.loc[1, column] = value
        with pytest.raises(ValueError, match=message):
            sampler.validate_workbook(bad)
    with pytest.raises(ValueError, match='missing'):
        sampler.validate_workbook(f.drop(columns='ACTUALE'))


def model(paths):
    return {'id': 'test', 'label': 'Fictional raster fixture', 'dataset': 'Fixture', 'version': '1',
            'datum': 'MSL', 'license': 'CC0-1.0', 'source_url': 'https://example.org/fixture', 'paths': paths}


def write_raster(path, values, crs='EPSG:4326', transform=None):
    rasterio = pytest.importorskip('rasterio')
    transform = transform or rasterio.transform.from_origin(0, 1, 1, 1)
    array = np.asarray([values], dtype='float32')
    with rasterio.open(path, 'w', driver='GTiff', width=len(values), height=1, count=1,
                       dtype='float32', crs=crs, transform=transform, nodata=-9999) as dst:
        dst.write(array, 1)


def test_raster_sampling_nodata_precedence_exclusion_and_missing(tmp_path):
    write_raster(tmp_path / 'first.tif', [0, -9999, -7, 3])
    write_raster(tmp_path / 'second.tif', [99, 1, 99, 99])
    frame = pd.DataFrame({'Longitude': [.5, 1.5, 2.5, 4, .5], 'Latitude': [.5]*5,
                          'coordinate_valid': [True, True, True, True, False]})
    values, status, sources, missing = sampler.sample_model(frame, model(['first.tif', 'absent.tif', 'second.tif']), tmp_path)
    np.testing.assert_allclose(values[:3], [0, 1, -7])
    assert status.tolist() == ['available', 'available', 'excluded_le_minus7', 'outside_coverage', 'invalid_coordinate']
    assert missing == 1 and len(sources) == 2
    assert screening_summary(values, 1)['available'] == 2
    _, absent, _, _ = sampler.sample_model(frame, model([]), tmp_path)
    assert absent[0] == 'missing_raster' and absent[-1] == 'invalid_coordinate'


def test_projected_raster_crs_and_already_msl_no_correction(tmp_path):
    rio = pytest.importorskip('rasterio')
    from rasterio.warp import transform
    x, y = transform('EPSG:4326', 'EPSG:3857', [.5], [.5])
    write_raster(tmp_path / 'projected.tif', [1.25], crs='EPSG:3857',
                 transform=rio.transform.from_origin(x[0]-50, y[0]+50, 100, 100))
    frame = pd.DataFrame({'Longitude': [.5], 'Latitude': [.5], 'coordinate_valid': [True]})
    values, status, _, _ = sampler.sample_model(frame, model(['projected.tif']), tmp_path)
    assert values[0] == 1.25 and status[0] == 'available'


def test_regional_crs_transform_failure_retains_valid_rows(tmp_path):
    rio = pytest.importorskip('rasterio')
    write_raster(tmp_path / 'utm.tif', [1.25], crs='EPSG:32632',
                 transform=rio.transform.from_origin(499950, 50, 100, 100))
    frame = pd.DataFrame({'Longitude': [9, 99], 'Latitude': [0, 0], 'coordinate_valid': [True, True]})
    values, status, _, _ = sampler.sample_model(frame, model(['utm.tif']), tmp_path)
    assert values[0] == 1.25 and np.isnan(values[1])
    assert status.tolist() == ['available', 'invalid_transform']
    result = screening_summary(values, 1)
    assert result['available'] == 1 and result['unavailable'] == 1 and result['total'] == 2


def test_multiband_nonidentity_scale_offset_decodes_before_screening(tmp_path):
    rio = pytest.importorskip('rasterio')
    path = tmp_path / 'encoded.tif'
    with rio.open(path, 'w', driver='GTiff', width=3, height=1, count=2, dtype='int16',
                  crs='EPSG:4326', transform=rio.transform.from_origin(0, 1, 1, 1), nodata=-9999) as dst:
        dst.write(np.array([[90, 91, 92]], dtype='int16'), 1)
        dst.write(np.array([[4, 6, -9999]], dtype='int16'), 2)
        dst.scales = (1, .5)
        dst.offsets = (0, -1)
    frame = pd.DataFrame({'Longitude': [.5, 1.5, 2.5], 'Latitude': [.5]*3, 'coordinate_valid': [True]*3})
    values, statuses, sources, _ = sampler.sample_model(frame, {**model(['encoded.tif']), 'band': 2}, tmp_path)
    np.testing.assert_allclose(values[:2], [1, 2])
    assert np.isnan(values[2]) and statuses.tolist() == ['available', 'available', 'nodata']
    assert sources[0]['scale'] == .5 and sources[0]['offset'] == -1
    summary = screening_summary(values, 1)
    assert summary['at_or_below'] == 1 and summary['above'] == 1 and summary['available'] == 2


def test_manifest_rejects_uncorrected_or_duplicate_models(tmp_path):
    path = tmp_path / 'manifest.json'
    for records in [[{**model([]), 'datum': 'EGM96'}], [model([]), model([])]]:
        path.write_text(json.dumps({'models': records}))
        with pytest.raises(ValueError):
            sampler.read_manifest(path)


def test_pipeline_only_publishes_aggregates(tmp_path, monkeypatch):
    pytest.importorskip('openpyxl')
    workbook = tmp_path / 'input.xlsx'
    workbook_frame().to_excel(workbook, sheet_name='Climate-Sites-w-coords', index=False)
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'models': [model([])]}))
    # Keep the real poster baseline for audit while directing private output to
    # a temporary private-data root; public fields are independently inspected.
    original_private = sampler.private_directory
    def test_private(path):
        path = tmp_path / 'private-data'
        path.mkdir(exist_ok=True)
        return path
    monkeypatch.setattr(sampler, 'private_directory', test_private)
    result = sampler.analyze(workbook, manifest, public_output=tmp_path / 'public')
    raw = (tmp_path / 'public/nature-aggregates.json').read_text()
    assert 'fixture-a' not in raw and '999' not in raw
    assert result['models'][0]['screening'][0]['total'] == 3
    assert result['models'][0]['screening'][0]['available'] == 0
    assert result['models'][0]['screening'][0]['at_or_below'] is None
    assert (tmp_path / 'private-data/samples.csv').exists()
    assert list((tmp_path / 'public').iterdir())
    with pytest.raises(ValueError, match='private-data'):
        original_private(ROOT / 'content')


def test_public_manifest_and_lesson_contract():
    sources = json.loads((ROOT / 'content/data/nature-sources.json').read_text(encoding='utf-8'))
    public = json.loads((ROOT / 'content/data/nature-aggregates.json').read_text(encoding='utf-8'))
    assert sources['catalog']['version_doi'] == '10.5281/zenodo.23341921'
    assert sources['addendum']['degrees'] == {'EGM96': 360, 'EGM2008': 2190, 'GOCO06s': 300}
    assert len(coverage_frame(public)) == len(public['models'])
    allowed = {p['source_url'] for p in sources['products']}
    for item in public['models']:
        assert item['source_url'] in allowed
        for result in item['screening']:
            if result['total'] is not None:
                assert result['available'] + result['unavailable'] == result['total']
            if not result['available']:
                assert result['at_or_below'] is None
        for pair in item.get('paired_original', []):
            if pair['matched']:
                assert sum(pair['cells'].values()) == pair['matched']
    forbidden = {'uid', 'latitude', 'longitude', 'ACTUALE', 'TXCURR23', 'CNTRYNAME'}
    def check_keys(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for v in value.values(): check_keys(v)
        elif isinstance(value, list):
            for v in value: check_keys(v)
    check_keys(public)
    for common in public.get('common_cohort', []):
        assert common['matched'] + common['unmatched'] == common['total']
        assert all(count is None if common['matched'] == 0 else 0 <= count <= common['matched']
                   for count in common['counts'].values())
    import nbformat
    index = json.loads((ROOT / 'content/lesson-index.json').read_text())
    for slug in ['14_vertical_datums', '15_nature_data_and_sampling', '16_facility_comparison', '17_datum_sensitivity']:
        assert slug in {item['slug'] for item in index}
        notebook = nbformat.read(ROOT / 'content/notebooks' / (slug + '.ipynb'), as_version=4)
        assert notebook.cells[-1].source == f"print('Nature lesson complete: {slug}')"
        assert any('piplite' in cell.source for cell in notebook.cells)
        text = '\n'.join(cell.source for cell in notebook.cells)
        assert '../source-audit.md' not in text and '../references.md' not in text and '../data-dictionary.md' not in text
        assert 'https://jltobias.github.io/JupyterLite-Sea-Level-Rise/book/source-audit.html' in text


def test_public_terrain_shapes_and_quality_mask():
    path = ROOT / 'content/data/nature-city-surfaces.json'
    if not path.exists():
        pytest.skip('Optional public terrain extracts are unavailable.')
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['license'] == 'CC-BY-NC-SA-4.0'
    assert len({(item['city'], item['model']) for item in data['cities']}) == len(data['cities'])
    for item in data['cities']:
        values = np.asarray(item['z_msl'], float)
        assert values.shape == (len(item['latitude']), len(item['longitude']))
        assert np.all(values[np.isfinite(values)] > -7)
        assert item['source_doi'].startswith('https://doi.org/10.17887/')
