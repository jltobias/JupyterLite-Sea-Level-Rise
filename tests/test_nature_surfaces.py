"""Ensure public terrain displays preserve the sampler's units and provenance."""
from pathlib import Path
import json
import sys
import numpy as np
import pytest

rio = pytest.importorskip('rasterio')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_nature_surfaces import prepare_surfaces
from analyze_nature import sha256


def source(paths, **overrides):
    return dict(id='fixture', label='Fictional fixture', dataset='Fixture', version='1',
                datum='MSL', unit='m', license='CC0-1.0', source_url='https://example.org',
                paths=paths, **overrides)


def manifest(tmp_path, models):
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(dict(models=models)))
    return path


def test_surface_selected_band_decoding_mask_and_provenance(tmp_path):
    path = tmp_path / 'encoded.tif'
    with rio.open(path, 'w', driver='GTiff', width=2, height=2, count=2,
                  dtype='int16', crs='EPSG:4326', nodata=-9999,
                  transform=rio.transform.from_origin(0, .3, .15, .15)) as dst:
        dst.write(np.full((2, 2), 100, dtype='int16'), 1)
        dst.write(np.array([[10, 20], [-9999, -80]], dtype='int16'), 2)
        dst.scales = (1, .1)
        dst.offsets = (0, 1)
    config = manifest(tmp_path, [source([path.name], band=2)])
    result = prepare_surfaces(config, [('Fictional city', .15, .15)])
    grid = result['cities'][0]['z_msl']
    assert grid == [[2, 3], [None, None]]
    provenance = result['provenance']
    assert provenance['manifest_sha256'] == sha256(config)
    recorded = provenance['source_files'][0]
    assert recorded['sha256'] == sha256(path)
    assert (recorded['band'], recorded['scale'], recorded['offset']) == (2, .1, 1)
    assert 'generated_utc' in provenance and 'rasterio' in provenance['software']
    assert str(tmp_path) not in json.dumps(result)


@pytest.mark.parametrize('field,value', [('datum', 'EGM96'), ('unit', 'ft')])
def test_surface_rejects_uncorrected_or_nonmetre_manifest(tmp_path, field, value):
    model = source([])
    model[field] = value
    with pytest.raises(ValueError, match='MSL'):
        prepare_surfaces(manifest(tmp_path, [model]), [])


def test_surface_missing_models_remain_unavailable(tmp_path):
    result = prepare_surfaces(manifest(tmp_path, [source([]),
        {**source(['absent.tif']), 'id': 'missing'}]), [('Fictional', 0, 0)])
    assert result['cities'] == []
    assert result['provenance']['model_coverage'] == [
        dict(model='fixture', available_files=0, missing_files=0, status='unavailable'),
        dict(model='missing', available_files=0, missing_files=1, status='unavailable')]
