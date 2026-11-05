"""Independent Nature 2026 teaching math and aggregate views (MIT).

No GIS, downloads, telemetry, or private file writes. All elevations are metres.
Static height thresholds describe screening exposure, never flood probability.
"""
from pathlib import Path
from html import escape
import io
import json
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
THRESHOLDS = (0.0, 1.0, 10.0)
EXCLUDE_AT_OR_BELOW = -7.0


def msl_elevation(h_egm, n_egm, n_goco06s, mdt):
    """H_MSL = H_EGM + N_EGM - N_GOCO06s - MDT; missing inputs propagate.

    Inputs must already share horizontal support, units, tide system and epoch.
    This arithmetic is not a geoid synthesis or an MHHW conversion.
    """
    return (np.asarray(h_egm, dtype=float) + np.asarray(n_egm, dtype=float)
            - np.asarray(n_goco06s, dtype=float) - np.asarray(mdt, dtype=float))


def valid_nature(values):
    values = np.asarray(values, dtype=float)
    return np.isfinite(values) & (values > EXCLUDE_AT_OR_BELOW)


def screening_summary(values, threshold=1.0, offset=0.0):
    """Keep original coverage fixed while shifting valid heights for sensitivity.

    The -7 m rule applies to the input, before a hypothetical shift. NoData and
    excluded cells cannot become dry or valid when a control changes.
    """
    if not np.isfinite(threshold) or not np.isfinite(offset):
        raise ValueError('Threshold and offset must be finite metres.')
    heights = np.asarray(values, dtype=float)
    if heights.ndim != 1:
        raise ValueError('One height per facility row is required.')
    valid = valid_nature(heights)
    available = int(valid.sum())
    below = int((heights[valid] + offset <= threshold).sum())
    return {'total': len(heights), 'available': available,
            'unavailable': len(heights) - available,
            'missing': int((~np.isfinite(heights)).sum()),
            'excluded_le_minus7': int((np.isfinite(heights) & ~valid).sum()),
            'threshold_m': float(threshold), 'offset_m': float(offset),
            'at_or_below': below if available else None,
            'above': available - below if available else None,
            'percent_of_available': 100 * below / available if available else None}


def paired_comparison(original_mhhw, nature_msl, threshold=1.0):
    """2x2 on paired rows; unlike datums preclude an accuracy interpretation."""
    old, new = np.asarray(original_mhhw, float), np.asarray(nature_msl, float)
    if old.ndim != 1 or old.shape != new.shape or not np.isfinite(threshold):
        raise ValueError('Paired one-dimensional arrays must have identical shapes and a finite threshold.')
    use = np.isfinite(old) & valid_nature(new)
    a, b = old[use] <= threshold, new[use] <= threshold
    cells = {'both_at_or_below': int((a & b).sum()),
             'original_only': int((a & ~b).sum()),
             'nature_only': int((~a & b).sum()),
             'neither': int((~a & ~b).sum())}
    return {'matched': int(use.sum()), 'unmatched': int((~use).sum()),
            'threshold_m': float(threshold),
            'original_zero_matched': int((old[use] == 0).sum()),
            'original_le_minus7_matched': int((old[use] <= -7).sum()),
            'cells': cells if use.any() else {k: None for k in cells},
            'interpretation': 'Raw, unverified original numeric audit: MHHW-labeled versus Nature MSL. Original zeros may be unassessed fill; no validated elevation, accuracy or pure datum-effect claim.'}


def flag_overlap(flags, nature_msl, threshold=1.0):
    """RCP categorical overlap on the same available rows, not ground truth."""
    if not np.isfinite(threshold):
        raise ValueError('Threshold must be finite metres.')
    flags = np.asarray(flags, dtype=object)
    heights = np.asarray(nature_msl, float)
    if flags.shape != heights.shape or heights.ndim != 1:
        raise ValueError('Flags and heights must be paired one-dimensional arrays.')
    if not np.isin(flags, ['RED', 'ORANGE', 'YELLOW', 'NOFILL']).all():
        raise ValueError('Unknown RCP category; expected RED, ORANGE, YELLOW or NOFILL.')
    # Binary -1/+1 encoding is only a shared matrix operation, not an elevation.
    flagged = np.isin(flags, ['RED', 'ORANGE', 'YELLOW'])
    use = valid_nature(heights)
    low = heights <= threshold
    cells = {'flag_and_low': int((use & flagged & low).sum()),
             'flag_only': int((use & flagged & ~low).sum()),
             'low_only': int((use & ~flagged & low).sum()),
             'neither': int((use & ~flagged & ~low).sum())}
    return {'matched': int(use.sum()), 'unmatched': int((~use).sum()),
            'cells': cells if use.any() else {k: None for k in cells},
            'interpretation': 'RCP flag overlap with a static MSL threshold; no accuracy score.'}


def common_model_comparison(model_heights, threshold=1.0):
    """Compare models on the intersection of their valid, identically ordered rows.

    Caller must supply arrays in the same supported uid order; no positional
    join of independently ordered exports is safe. Empty coverage stays null.
    """
    if not model_heights or not np.isfinite(threshold):
        raise ValueError('At least one model and a finite threshold are required.')
    arrays = {key: np.asarray(value, dtype=float) for key, value in model_heights.items()}
    first = next(iter(arrays.values()))
    if first.ndim != 1 or any(a.ndim != 1 or a.shape != first.shape for a in arrays.values()):
        raise ValueError('All model arrays must have identical one-dimensional supported-row order and shape.')
    matched = np.logical_and.reduce([valid_nature(a) for a in arrays.values()])
    n = int(matched.sum())
    return {'total': len(first), 'matched': n, 'unmatched': len(first) - n,
            'threshold_m': float(threshold),
            'counts': {key: int((a[matched] <= threshold).sum()) if n else None for key, a in arrays.items()},
            'interpretation': 'Same supported rows valid in every listed model; static MSL screening, not accuracy or a full-portfolio estimate.'}


def load_public():
    return json.loads((DATA / 'nature-aggregates.json').read_text(encoding='utf-8'))


def load_sources():
    return json.loads((DATA / 'nature-sources.json').read_text(encoding='utf-8'))


def fictional_samples():
    """Small invented fixture, independent of study data or geographic locations."""
    heights = [-7, -1, 0, .4, 1, 2, 5, 10, 12, np.nan]
    return pd.DataFrame({'uid': [f'FICTIONAL-{i:02d}' for i in range(10)],
                         'model': 'fictional', 'msl_m': heights,
                         'original_mhhw_m': [-6, -.5, .5, 1.2, 1.5, 2.5, 5.5, 10.5, 12.5, 3]})


def read_sample_csv(data):
    """Read a deliberately uploaded local CSV in memory; retain approved columns.

    Schema: uid, model, msl_m; optional original_mhhw_m. One supported row per
    uid/model. The local pipeline has already applied the support filter.
    """
    frame = pd.read_csv(io.BytesIO(bytes(data)), dtype={'uid': str, 'model': str})
    required = {'uid', 'model', 'msl_m'}
    if not required <= set(frame.columns):
        raise ValueError('Required CSV columns: uid, model, msl_m.')
    for key in ['uid', 'model']:
        frame[key] = frame[key].str.strip()
    if frame[['uid', 'model']].isna().any().any() or frame.uid.eq('').any() or frame.model.eq('').any():
        raise ValueError('CSV uid and model must be nonempty.')
    if frame.duplicated(['uid', 'model']).any():
        raise ValueError('Duplicate uid/model rows would inflate the denominator.')
    for name in ['msl_m', 'original_mhhw_m']:
        if name in frame:
            frame[name] = pd.to_numeric(frame[name], errors='raise')
    return frame[[c for c in ['uid', 'model', 'msl_m', 'original_mhhw_m'] if c in frame]].copy()


def coverage_frame(public=None, threshold=1):
    public = load_public() if public is None else public
    rows = []
    for model in public['models']:
        s = next(s for s in model['screening'] if s['threshold_m'] == threshold)
        rows.append({'model': model['label'], 'status': model['status'], **s})
    return pd.DataFrame(rows)


def terrain_explorer():
    """Optional public terrain extracts, never facility points or private samples."""
    path = DATA / 'nature-city-surfaces.json'
    if not path.exists():
        print('Public terrain extracts unavailable. No real raster surface is claimed or substituted.')
        return None
    import ipywidgets as w
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from IPython.display import display
    from coastlab import show
    payload = json.loads(path.read_text(encoding='utf-8'))
    entries = payload.get('cities', [])
    if not entries:
        print('No public terrain extracts available.')
        return None
    start = next((i for i, c in enumerate(entries) if c['city'] == 'Bangkok' and 'FABDEM' in c['model']), 0)
    select = w.Dropdown(options=[(f'{c["city"]} — {c["model"]}', i) for i, c in enumerate(entries)],
                        value=start, description='Terrain:', layout=w.Layout(width='95%'))
    notice, output = w.HTML(), w.Output()
    output.add_class('nature-terrain-output')

    def update(*_):
        item = entries[select.value]
        z = np.asarray(item['z_msl'], dtype=float)
        if z.shape != (len(item['latitude']), len(item['longitude'])):
            raise ValueError('Terrain grid must have latitude rows and longitude columns.')
        # Retain the same Nature quality boundary in educational terrain views.
        z = np.where(valid_nature(z), z, np.nan)
        notice.value = (f'<p class="nature-terrain-view">PUBLIC TERRAIN: {escape(item["city"])}; '
                        f'{escape(item["model"])}. {escape(item["grid_note"])}. '
                        f'Source: {escape(item["source_doi"])}. No facility locations; no inundation model.</p>')
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'xy'}, {'type': 'surface'}]],
                            subplot_titles=['MSL terrain height', 'Same terrain in 3D; vertical exaggeration'])
        fig.add_trace(go.Heatmap(x=item['longitude'], y=item['latitude'], z=z,
                                colorscale='Viridis', colorbar_title='m MSL', showscale=True), row=1, col=1)
        fig.add_trace(go.Surface(x=item['longitude'], y=item['latitude'], z=z,
                                colorscale='Viridis', showscale=False), row=1, col=2)
        fig.update_layout(title='Public terrain context: ' + item['city'],
                          xaxis_title='Longitude', yaxis_title='Latitude',
                          scene=dict(xaxis_title='Longitude', yaxis_title='Latitude', zaxis_title='m MSL'))
        with output:
            output.clear_output(wait=True)
            show(fig)
            display(pd.DataFrame({'available_display_cells': [int(np.isfinite(z).sum())],
                                  'missing_or_excluded_cells': [int((~np.isfinite(z)).sum())]}))
    select.observe(update, names='value')
    update()
    ui = w.VBox([select, notice, output])
    display(ui)
    return ui


def aggregate_explorer(public=None):
    """Public-only threshold controls; source-unavailable stays visible."""
    import ipywidgets as w
    import plotly.graph_objects as go
    from IPython.display import display
    from coastlab import show
    public = load_public() if public is None else public
    model = w.Dropdown(options=[(m['label'], m['id']) for m in public['models']], description='Model:')
    threshold = w.Dropdown(options=[('0 m', 0), ('1 m', 1), ('10 m', 10)], value=1, description='Threshold:')
    card, output = w.HTML(), w.Output()
    output.add_class('nature-public-output')

    def update(*_):
        record = next(m for m in public['models'] if m['id'] == model.value)
        result = next(s for s in record['screening'] if s['threshold_m'] == threshold.value)
        n = result['at_or_below']
        count = 'unavailable' if n is None else str(n)
        card.value = (f'<p class="nature-public-card"><strong>{escape(record["label"])}</strong>: '
                      f'height ≤ {threshold.value} m MSL: {count}; available {result["available"]}; '
                      f'cohort {result["total"] if result["total"] is not None else "not yet audited"}. '
                      f'Status: {escape(record["status"])}. Static screening, not flood probability.</p>')
        with output:
            output.clear_output(wait=True)
            if n is None:
                print('No sampled results available for this model. Pending coverage is not zero exposure.')
            else:
                show(go.Figure(go.Bar(x=['At/below threshold', 'Above threshold', 'Unavailable'],
                                     y=[n, result['above'], result['unavailable']],
                                     marker_color=['#087e8b', '#c1d7d9', '#e3a938'])).update_layout(
                                         title='Supported portfolio: static height screening', yaxis_title='Facilities'))
    for control in [model, threshold]:
        control.observe(update, names='value')
    update()
    ui = w.VBox([w.HBox([model, threshold]), card, output])
    ui.controls = {'model': model, 'threshold': threshold, 'card': card}
    display(ui)
    return ui


def sensitivity_controls(allow_upload=False):
    """Interactive invented example; an optional upload stays in browser memory.

    No network APIs or file writes occur here. Downloaded/saved notebooks can
    retain outputs, so do not publish a notebook after using private input.
    """
    import ipywidgets as w
    import plotly.graph_objects as go
    from IPython.display import display
    from coastlab import show
    state = {'frame': fictional_samples(), 'label': 'FICTIONAL demo'}
    model = w.Dropdown(options=['fictional'], description='Model:')
    threshold = w.FloatSlider(value=1, min=0, max=10, step=.25, description='Height ≤ m:', continuous_update=False)
    offset = w.FloatSlider(value=0, min=-2, max=2, step=.1, description='Shift m:', continuous_update=False)
    card, output, notice = w.HTML(), w.Output(), w.HTML()
    output.add_class('nature-sensitivity-output')

    def update(*_):
        subset = state['frame'].loc[state['frame'].model == model.value]
        values = subset.msl_m.to_numpy()
        s = screening_summary(values, threshold.value, offset.value)
        card.value = (f'<p class="nature-sensitivity-card"><strong>{state["label"]}</strong>: '
                      f'height ≤ {threshold.value:g} m; shift {offset.value:+.1f} m; '
                      f'at/below {s["at_or_below"]}; available {s["available"]}/{s["total"]}; '
                      f'unavailable {s["unavailable"]}. No probability or future-year interpretation.</p>')
        shifts = np.linspace(-2, 2, 41)
        counts = [screening_summary(values, threshold.value, x)['at_or_below'] for x in shifts]
        with output:
            output.clear_output(wait=True)
            fig = go.Figure(go.Scatter(x=shifts, y=counts, mode='lines', name='Screened count'))
            fig.add_scatter(x=[offset.value], y=[s['at_or_below']], mode='markers', marker_size=12, name='Selected shift')
            fig.update_layout(title=state['label'] + ': fixed-coverage height sensitivity',
                              xaxis_title='Hypothetical height shift (m)', yaxis_title='Facilities at/below threshold')
            show(fig)
    for control in [model, threshold, offset]:
        control.observe(update, names='value')
    children = [w.HTML('<p>Shift changes valid heights only. The input exclusion and denominator stay fixed.</p>'),
                model, threshold, offset, card, output]
    if allow_upload:
        upload = w.FileUpload(accept='.csv', multiple=False, description='Local sample CSV')
        reset = w.Button(description='Restore fictional demo')

        def restore(*_):
            upload.value = ()
            state.update(frame=fictional_samples(), label='FICTIONAL demo')
            model.options = ['fictional']
            threshold.value = 1
            offset.value = 0
            notice.value = ''
            update()

        def uploaded(change):
            if not upload.value:
                return
            item = next(iter(upload.value.values())) if isinstance(upload.value, dict) else upload.value[0]
            try:
                frame = read_sample_csv(item['content'])
                if frame.empty:
                    raise ValueError('The sample CSV is empty.')
                state.update(frame=frame, label='PRIVATE uploaded samples — local session only')
                model.options = sorted(frame.model.unique())
                notice.value = ('<p>Local CSV loaded; upload bytes are cleared after processing. '
                                'Do not save/publish these notebook outputs. In JupyterLite, reload the page '
                                'to end the browser kernel session. In local/server Jupyter, restart or '
                                'shut down the kernel; reloading the page does not clear that kernel.</p>')
                update()
            except (ValueError, TypeError, UnicodeError, pd.errors.ParserError):
                notice.value = '<p role="alert">Invalid CSV: require uid, model, numeric msl_m and unique uid/model rows. Existing data retained.</p>'
            finally:
                # FileUpload.value is serialized in saved widget state. Retain
                # only the parsed dataframe in this closure's kernel state.
                upload.value = ()
        upload.observe(uploaded, names='value')
        reset.on_click(restore)
        children.extend([w.HTML('<p>Optional private upload is processed in this kernel only; no external transmission. A local/server kernel runs on that server. JupyterLite runs in your browser.</p>'), upload, reset, notice])
    update()
    ui = w.VBox(children)
    ui.controls = {'threshold': threshold, 'offset': offset, 'model': model, 'card': card}
    if allow_upload:
        ui.controls.update(upload=upload, reset=reset, notice=notice)
    display(ui)
    return ui
