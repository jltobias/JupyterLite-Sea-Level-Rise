"""Transparent teaching calculations. These are NOT Climate Central/PAT outputs."""
from pathlib import Path
import math
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
SCENARIOS = ('RCP 2.6', 'RCP 4.5', 'RCP 8.5')
YEARS = tuple(range(2020, 2101, 10))
COLORS = {'RCP 2.6': '#087e8b', 'RCP 4.5': '#b26b00', 'RCP 8.5': '#cb4260'}

def load_data():
    """Return fictional facility dimension and scenario-year exposure fact table."""
    facilities = pd.read_csv(DATA / 'synthetic_facilities.csv')
    exposure = pd.read_csv(DATA / 'synthetic_exposure.csv')
    validate(facilities, exposure)
    return facilities, exposure

def validate(facilities, exposure):
    if facilities.facility_id.duplicated().any():
        raise ValueError('Facility IDs must be unique in the dimension table.')
    if exposure.duplicated(['facility_id', 'scenario', 'year']).any():
        raise ValueError('Duplicate facility/scenario/year keys inflate counts.')
    if not set(exposure.facility_id) <= set(facilities.facility_id):
        raise ValueError('Exposure includes unknown facility IDs.')
    if not exposure.annual_probability.between(0, 1).all():
        raise ValueError('Probability must be a fraction in [0, 1], with no missing values.')
    if not set(exposure.scenario) <= set(SCENARIOS) or not set(exposure.year) <= set(YEARS):
        raise ValueError('Unexpected scenario or decade.')
    expected = len(facilities) * len(SCENARIOS) * len(YEARS)
    if len(exposure) != expected:
        raise ValueError('The bundled teaching panel must be complete.')
    if not facilities.longitude.between(-180, 180).all() or not facilities.latitude.between(-90, 90).all():
        raise ValueError('Invalid WGS84 coordinate.')

def toy_slr(scenario, year):
    """Arbitrary metres above a fictional 2020 baseline; NOT an IPCC projection."""
    if scenario not in SCENARIOS or not 2020 <= year <= 2100:
        raise ValueError('Use a supported RCP label and year from 2020 to 2100.')
    t = (year - 2020) / 80
    endpoint = {'RCP 2.6': 0.45, 'RCP 4.5': 0.65, 'RCP 8.5': 1.0}[scenario]
    return 0.20 * t + (endpoint - 0.20) * t * t

def toy_probability(elevation_m, slr_m, surge_m=0.7, scale_m=0.55):
    """Logistic teaching response to water minus elevation; no flood calibration."""
    if scale_m <= 0:
        raise ValueError('scale_m must be positive')
    z = np.clip((np.asarray(elevation_m) - slr_m - surge_m) / scale_m, -700, 700)
    return 1.0 / (1.0 + np.exp(z))

def select(facilities, exposure, scenario='RCP 2.6', year=2030,
           country='All', city='All', supported_only=False, service_type='All'):
    f = facilities.copy()
    if country != 'All': f = f[f.country == country]
    if city != 'All': f = f[f.city == city]
    if service_type != 'All': f = f[f.service_type == service_type]
    if supported_only: f = f[f.pepfar_demo == 1]
    e = exposure[(exposure.scenario == scenario) & (exposure.year == year)]
    return f.merge(e, on='facility_id', validate='one_to_one')

def cards(rows, threshold=0.1):
    if not 0 <= threshold <= 1: raise ValueError('Threshold must be in [0, 1].')
    if rows.facility_id.duplicated().any():
        raise ValueError('Cards require exactly one scenario and year per facility.')
    exposed = rows[rows.annual_probability >= threshold]
    return {'facilities': len(rows), 'above_threshold': len(exposed),
            'share_percent': 100 * len(exposed) / len(rows) if len(rows) else 0.0,
            'service_load_at_exposed': int(exposed.service_load.sum()),
            'expected_exposed': float(rows.annual_probability.sum())}

def cumulative_probability(probabilities):
    """At least one exceedance; requires annual inputs and independence assumption."""
    p = np.asarray(probabilities, dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError('Every annual probability must be finite and in [0, 1].')
    return float(1 - np.prod(1 - p))

def haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = np.radians([lon1, lat1, lon2, lat2])
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return float(6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))

def site_url(path):
    """Use absolute URLs in Lite, whose output renderer rewrites relative links as files."""
    import sys
    if sys.platform == 'emscripten':
        from js import location
        worker_url = str(location.href)
        if '/lite/' in worker_url:
            return worker_url.split('/lite/', 1)[0] + '/' + path.lstrip('/')
        raise RuntimeError('Expected the deployed /lite/ runtime path to locate static assets.')
    return '../../' + path.lstrip('/')

def show(fig):
    """Same local Plotly bundle in book and Lite; HTML iframe avoids renderer extensions."""
    from IPython.display import display_html
    import html
    # Both /book/notebooks/ and /lite/lab/ are two levels below the site root.
    doc = fig.to_html(full_html=True, include_plotlyjs=site_url('assets/plotly.min.js'),
                      config={'responsive': True, 'displaylogo': False})
    display_html('<iframe title="Interactive teaching figure" style="width:100%;height:560px;border:0" '
                 'srcdoc="' + html.escape(doc, quote=True) + '"></iframe>', raw=True)

def dashboard(view='map', scenario='RCP 2.6', dataset='poster'):
    from IPython.display import display_html
    from urllib.parse import urlencode
    query = urlencode({'view': view, 'scenario': scenario, 'dataset': dataset})
    url = site_url('dashboard/index.html') + '?' + query
    display_html(f'<p><a href="{url}" target="_blank">Open full-screen dashboard</a></p>'
                 f'<iframe title="Fictional coastal facilities dashboard" src="{url}" '
                 'style="width:100%;height:960px;border:1px solid #cbd9de;border-radius:12px"></iframe>', raw=True)

def land_traces():
    import json
    import plotly.graph_objects as go
    land = json.loads((DATA / 'natural-earth-land.geojson').read_text())
    xs, ys = [], []
    for feature in land['features']:
        geometry = feature['geometry']
        polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        for polygon in polygons:
            for ring in polygon:
                xs.extend([p[0] for p in ring] + [None]); ys.extend([p[1] for p in ring] + [None])
    return [go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='#859a9e', width=0.6),
                       hoverinfo='skip', showlegend=False, name='Natural Earth land')]
