"""Author only chapters 14–17; safe to call without regenerating earlier lessons."""
from pathlib import Path
import json
import textwrap
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
LESSONS = [
    ('14_vertical_datums', 'Vertical datums: what does zero metres mean?', 40),
    ('15_nature_data_and_sampling', 'Nature 2026: sources, sampling and coverage', 45),
    ('16_facility_comparison', 'Compare facility screening with the AIDS 2024 baseline', 45),
    ('17_datum_sensitivity', 'Datum sensitivity and a defensible interpretation', 40),
]


def md(text):
    return nb.v4.new_markdown_cell(textwrap.dedent(text).strip())


def code(text):
    return nb.v4.new_code_cell(textwrap.dedent(text).strip())


SETUP = '''
import sys
from pathlib import Path
if sys.platform == 'emscripten':
    import piplite
    await piplite.install(['numpy', 'pandas', 'plotly', 'ipywidgets'])
root = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(root))
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import display
from coastlab import show, land_traces
from naturelab import (msl_elevation, screening_summary, paired_comparison,
                       load_public, load_sources, coverage_frame, fictional_samples,
                       aggregate_explorer, sensitivity_controls, terrain_explorer)
public = load_public()
sources = load_sources()
print('Ready: Nature 2026 — public aggregates and explicitly fictional exercises.')
print('Current sampling status:', public['status'])
'''

SOURCES = '''
## Sources and evidence boundaries

Seeger & Minderhoud (2026), [*Sea level much higher than assumed in most coastal hazard assessments*](https://doi.org/10.1038/s41586-026-10196-1), with the [25 August 2026 addendum](https://doi.org/10.1038/s41586-026-11017-1). The pinned [October 2026 catalog, record 23341921](https://doi.org/10.5281/zenodo.23341921) describes corrected products and their licenses. Exact versions, URLs, roles and inspected metadata hashes are in `data/nature-sources.json`; current results are in `data/nature-aggregates.json`.

Original calculations/code here are independent MIT implementations. Corrected-raster derivatives are **CC BY-NC-SA 4.0**, distinct from the **CC BY 4.0** original lesson prose and paper. Cite the corrected product, underlying DEM and MDT/geoid sources. No private workbook, facility identifiers, names, coordinates or clinical counts are bundled. [Full source audit](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/book/source-audit.html) · [Data dictionary](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/book/data-dictionary.html) · [References](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/book/references.html).
'''


def lesson14():
    return [md('''
    ## Objectives: distinguish the reference from the quantity

    Explain ellipsoid, geoid, mean sea level (MSL) and mean higher high water (MHHW). Check the sign of a datum conversion. Identify when a conversion would be applied twice.

    A height needs a reference surface. A benchmark reading of 1 m does not identify the surface called zero, its epoch, or whether the height describes a roof, canopy, terrain or water. The same physical point can have different numeric heights in different reference systems.

    | Symbol or term | Meaning in this lesson |
    |---|---|
    | Ellipsoid | Smooth mathematical reference used for positioning |
    | Geoid, N | Gravity-based reference surface, described here by height above the ellipsoid |
    | H_EGM | Terrain height relative to an EGM geoid |
    | MDT | Mean dynamic topography: mean sea-surface height above its specified geoid |
    | H_MSL | Terrain height relative to the mean sea surface |
    | MHHW | Mean of daily higher high waters over a tidal reference period; different from MSL |

    A geoid is not everywhere identical to the time-averaged ocean surface. The Nature extension asks what a correctly referenced terrain model adds to facility screening. It does not turn a static DEM into a flood forecast.
    '''), md(r'''
    ## Follow the signs through one physical height

    First recover a common ellipsoidal height, then subtract the sea surface:

    \[
    h = H_{EGM} + N_{EGM},\qquad
    H_{MSL}=H_{EGM}+N_{EGM}-N_{GOCO06s}-MDT.
    \]

    These are compatible, colocated inputs in metres, not a recipe for combining arbitrary grids. Holding the terrain and geoids fixed, a larger MDT means a higher mean sea surface and a **smaller** terrain height above it. The example below is invented solely to check that sign.
    '''), code('''
    example = pd.DataFrame({'H_EGM_m': [1.8, 1.8, 1.8],
                            'N_EGM_m': [30.4]*3, 'N_GOCO06s_m': [30.0]*3,
                            'MDT_m': [0.0, 0.4, 0.8]})
    example['H_MSL_m'] = msl_elevation(example.H_EGM_m, example.N_EGM_m,
                                      example.N_GOCO06s_m, example.MDT_m)
    display(example)
    assert np.allclose(example.H_MSL_m, [2.2, 1.8, 1.4])
    show(go.Figure(go.Scatter(x=example.MDT_m, y=example.H_MSL_m, mode='lines+markers'))
         .update_layout(title='FICTIONAL sign check: raising the sea lowers relative terrain height',
                        xaxis_title='MDT above GOCO06s (m)', yaxis_title='Terrain above MSL (m)'))
    '''), md('''
    ## The input contract matters as much as the formula

    HYBRID-CNES-CLS2022 uses GOCO06s and averages 1993–2021. The addendum specifies tide-free geoid calculations, the zero-degree term, and degrees 360 / 2190 / 300 for EGM96 / EGM2008 / GOCO06s. The helper evaluates arithmetic only; it does **not** recreate those geoid fields, interpolation or MDT extrapolation.

    The repository consumes authors' already-MSL rasters. Applying the equation again would double-correct them. The historical workbook's `ACTUALE` is modeled as `ACTUAL_MHHW_ELEV_M`; it is not established as an EGM-referenced input. Subtracting MDT from it without the tidal-reference relationship is unjustified. An MHHW-to-MSL relationship must be documented for the place and reference period.

    ## Lab: diagnose three workflows

    1. An analyst has H_EGM=1.8, N_EGM=30.4, N_GOCO06s=30.0 and MDT=0.8 m. Compute the result and explain each sign.
    2. Another analyst receives a TIFF explicitly referenced to MSL and subtracts MDT again. Explain the error.
    3. A report calls its original height MHHW and a new height MSL. What extra evidence is necessary before interpreting their difference as a datum change?

    **Worked answers:** (1) 1.4 m: recover ellipsoidal terrain and subtract the mean sea surface. (2) The sea-level adjustment was already included. (3) Obtain the local tidal-datum relation and epochs; also investigate terrain source, resolution and acquisition time. Their difference alone cannot isolate datum effects.

    **Deliverable:** A four-line provenance label stating quantity, unit, reference surface and epoch for each input. Write “unknown” wherever documentation is absent.
    ''')]


def lesson15():
    return [md('''
    ## Objectives: make the denominator reproducible

    Distinguish a catalog from raster data, pin versions and rights, and explain every missing cell. Follow an authorized workbook through validation, sampling and aggregate publication.

    The October 2026 catalog lists **FABDEM v1.0**, **DeltaDTM v1.1**, and **GLL-DTMv2** corrected to MSL. The paper calls DeltaDTM **v1**; the current catalog's **v1.1** must be named explicitly when used. GLL's approximately 1 km grid is a portfolio screening input, not a building survey. Inspect actual raster CRS and cell size rather than inferring them from a filename.

    The original public GLL v2 release is not an interchangeable fallback: the Nature methods identify a prior geoid-conversion error and describe obtaining a preconverted EGM96 version from the authors. This workflow uses the corrected WUR product, not an ad hoc correction of the public original.
    '''), code('''
    catalog = pd.DataFrame(sources['products'])
    display(catalog[['id', 'dataset', 'version', 'datum', 'source_url', 'license']])
    print('Catalog version:', sources['catalog']['version_doi'])
    display(coverage_frame(public)[['model', 'status', 'total', 'available', 'unavailable', 'at_or_below']])
    print('Null means unavailable, not zero. Threshold shown: <=1 m MSL.')
    '''), md('''
    ## Inspect public terrain context

    When available, the following city selector displays real raster-derived terrain in 2D and 3D. Its grid note identifies the source model and display sampling. These public geographic extracts are independent of the private facility table: no facility points are plotted. Null cells and heights ≤−7 m stay masked. The 3D aspect ratio exaggerates height; the paired map is the 2D alternative. A terrain surface alone has no hydraulic connectivity, defenses, flood extent or probability.
    '''), code('''
    terrain = terrain_explorer()
    '''), md('''
    ## A local pipeline with an auditable handoff

    1. Use an authorized local copy of the `Climate-Sites-w-coords` worksheet. Validate required columns, unique `uid` and 0/1 `PEPFARSUP`. Select supported rows once.
    2. Audit all 24 RCP scenario/decade counts against the published baseline. Invalid categories stop processing; discrepancies remain explicit.
    3. Keep invalid coordinates in the denominator. For valid WGS84 longitude/latitude, transform into each raster CRS. Sample the **containing pixel**, with no interpolation or extrapolation. Apply the raster band's scale/offset. At an internal pixel boundary, rasterio's row/column convention selects the lower/right cell.
    4. For overlapping tiles, use the first finite unmasked value in manifest order. NoData can fall through to another tile. Heights ≤−7 m are excluded; their raw values and reason remain private. Missing rasters, outside coverage and invalid coordinates remain unavailable.
    5. Write detailed samples/audit only to ignored `private-data/`. Publish model metadata, coverage and whole-portfolio aggregates. Hash sources and record the generation time.

    This deterministic point sampler is independent of the paper's global analysis and does not replicate its bilinear coastal sampling, water masking or geoid construction. A point inside a coarse cell inherits that cell's uncertainty.

    **Local terminal, optional; never run as a browser dependency:**

    ```bash
    python -m pip install -r requirements-geospatial.txt
    python scripts/analyze_nature.py private-data/sites.xlsx --manifest private-data/nature-rasters.json
    python scripts/update_provenance.py
    ```

    See the [source audit](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/book/source-audit.html) for the manifest template and column overrides. Raster acquisition is explicit and separate; a default lesson never downloads large grids.
    '''), code('''
    edge = np.array([-8, -7, -6.9, 0, 1, 10, 10.1, np.nan])
    checks = pd.DataFrame([screening_summary(edge, t) for t in [0, 1, 10]])
    print('FICTIONAL boundary fixture; not sampled facilities')
    display(checks)
    assert checks.at_or_below.tolist() == [2, 3, 4]
    assert (checks.available + checks.unavailable == checks.total).all()
    assert (checks.excluded_le_minus7 == 2).all()
    show(go.Figure(go.Bar(x=['<=0 m', '<=1 m', '<=10 m'], y=checks.at_or_below))
         .update_layout(title='FICTIONAL thresholds include equality; 3 of 8 rows unavailable',
                        yaxis_title='Valid rows at/below threshold'))
    '''), md('''
    ## Lab: missingness is a result

    A model has eight portfolio rows: two are excluded at ≤−7 m, one is NoData and five are valid. Four valid heights are ≤10 m. Compute the share among available rows and the share of the full cohort known to be ≤10 m. Can the other three be described as dry?

    **Worked answer:** 4/5=80% among available rows, while 4/8=50% of the full cohort are known to satisfy the threshold. Three rows are unavailable, so neither 50% nor 80% is a complete-cohort flood probability. If all cells are unavailable, the count is reported as unavailable, not zero.

    **Deliverable:** A coverage ledger conserving `available + unavailable = total`, with reasons for unavailable rows, exact raster versions, interpolation choice and source hashes. Explain why two model totals on different covered cohorts cannot be ranked as if they measured the same facilities.
    ''')]


def lesson16():
    return [md('''
    ## Objectives: compare like rows and unlike questions honestly

    Reconcile the AIDS 2024 baseline, inspect model-specific coverage, and interpret a matched 2×2 table without calling disagreement an error. No private facility points appear in this chapter.

    The historical poster asks about potentially flooded facilities under RCP/year categories. The new screening asks whether sampled terrain is at or below a fixed MSL threshold. No year or RCP is attached to the latter. A value ≤1 m is neither an RCP 8.5 forecast nor a 1% annual chance of flooding.
    '''), code('''
    poster = pd.read_csv(root / 'data/poster_aggregates.csv')
    baseline = poster.loc[poster.scope.eq('portfolio')]
    display(baseline.pivot(index='year', columns='scenario', values='potentially_flooded'))
    fig = go.Figure()
    for scenario, rows in baseline.groupby('scenario'):
        fig.add_scatter(x=rows.year, y=rows.potentially_flooded, mode='lines+markers', name=scenario)
    show(fig.update_layout(title='AIDS 2024 published portfolio categories; denominator 25,873',
                           xaxis_title='Projection year', yaxis_title='Published potentially flooded facilities'))
    audit = public.get('baseline_audit')
    if audit is None:
        print('Current Nature sampling run has not audited the private workbook yet.')
    else:
        print('Current workbook: all24 counts match:', audit['all_24_match'],
              '; denominator matches:', audit['denominator_matches'])
        display(pd.DataFrame(audit['counts']))
    '''), md('''
    ## Public geographic context

    The map below computes 2030 counts from the published **city** rows only. Its points are approximate city anchors; marker size represents a published city aggregate. It provides geographic context and is not a map of sampled facilities or of Nature raster coverage. City and district scopes must never be added together.
    '''), code('''
    cities = poster.loc[poster.scope.eq('city') & poster.scenario.eq('RCP 8.5') & poster.year.eq(2030)]
    fig = go.Figure(land_traces())
    fig.add_scatter(x=cities.longitude, y=cities.latitude, mode='markers+text',
                    text=cities.city, textposition='top center',
                    marker=dict(size=8 + 3*np.sqrt(cities.potentially_flooded), color='#087e8b'),
                    customdata=cities[['potentially_flooded', 'facilities_2023']].to_numpy(),
                    hovertemplate='%{text}<br>Published: %{customdata[0]} / %{customdata[1]}<extra></extra>')
    show(fig.update_layout(title='Published city aggregates, RCP 8.5 / 2030 — contextual city anchors',
                           xaxis_title='Longitude', yaxis_title='Latitude', showlegend=False,
                           xaxis_range=[-25, 125], yaxis_range=[-20, 40], yaxis_scaleanchor='x'))
    '''), code('''
    display(coverage_frame(public))
    public_controls = aggregate_explorer(public)
    '''), md('''
    ## Same-row comparison, different references

    The primary comparison is the **audited RCP flags** versus static MSL screening. Original `ACTUALE` contains numerous zeros and some very negative numeric values. Zero may mean an unassessed/fill value rather than valid terrain at the reference surface. Its meaning requires source metadata; finite numeric values alone do not establish valid elevations.

    The optional original-height audit pairs **the same supported rows with finite original numbers and valid Nature heights**. A 2×2 table then describes raw numeric thresholds only. It is disabled below unless `ENABLE_RAW_ORIGINAL_AUDIT` is explicitly enabled. Zero and extreme-negative counts remain visible in the audit. The original is MHHW-labeled and the new product is MSL: agreement is not accuracy, and disagreement cannot be attributed solely to datum. Terrain measurement, epoch and spatial resolution also change.

    RCP cross-tabs likewise describe overlap with RED/ORANGE/YELLOW flags, not sensitivity/specificity against observed flooding. Missing new elevations are excluded from both sides of the paired table and counted as unmatched. The sum of its four cells must equal `matched`.

    First inspect **per-model covered cohorts**. A partial regional FABDEM sample and a broader GLL sample may include different rows. Their individual absolute counts cannot establish which model has more exposure. The across-model chart below first intersects the supported rows with valid cells in **every** listed model. It uses this smaller, common denominator for all models and keeps the unmatched portfolio visible. It still does not measure accuracy or establish representativeness beyond that shared subset.
    '''), code('''
    ENABLE_RAW_ORIGINAL_AUDIT = False
    original_audit = public.get('original_elevation_audit')
    if original_audit:
        print(original_audit['interpretation'])
        display(pd.DataFrame([{k: v for k, v in original_audit.items() if k != 'interpretation'}]))
    common = public.get('common_cohort', [])
    if common and common[0]['matched']:
        common_rows = [{'model': model_id, 'threshold_m': item['threshold_m'],
                        'at_or_below': count, 'matched': item['matched'], 'unmatched': item['unmatched']}
                       for item in common for model_id, count in item['counts'].items()]
        common_table = pd.DataFrame(common_rows)
        display(common_table)
        fig = go.Figure()
        for model_id, rows in common_table.groupby('model'):
            metadata = next(m for m in public['models'] if m['id'] == model_id)
            fig.add_bar(x=rows.threshold_m.astype(str), y=rows.at_or_below,
                        name=metadata['dataset'] + ' v' + metadata['version'])
        show(fig.update_layout(barmode='group',
                               title=f"Shared supported cohort: {common[0]['matched']} matched; {common[0]['unmatched']} unmatched",
                               xaxis_title='Static MSL threshold (m)', yaxis_title='Facilities at/below threshold'))
    else:
        print('Common-model cohort unavailable; no cross-model count comparison is made.')
    for model in public['models']:
        print(model['label'], '—', model['status'])
        paired = next((p for p in model.get('paired_original', []) if p['threshold_m'] == 1), None)
        if not ENABLE_RAW_ORIGINAL_AUDIT:
            print('Raw original numeric audit disabled; original zero/fill semantics are unverified.')
        elif paired is None or not paired['matched']:
            print('Matched original/Nature comparison unavailable; no matrix is invented.')
        else:
            assert sum(paired['cells'].values()) == paired['matched']
            display(pd.DataFrame([{'matched': paired['matched'], 'unmatched': paired['unmatched'], **paired['cells']}]))
            c = paired['cells']
            z = [[c['both_at_or_below'], c['original_only']], [c['nature_only'], c['neither']]]
            show(go.Figure(go.Heatmap(z=z, x=['Nature <=1 m MSL', 'Nature >1 m MSL'],
                                     y=['Original <=1 m MHHW', 'Original >1 m MHHW'],
                                     text=z, texttemplate='%{text}', colorscale='Blues'))
                 .update_layout(title=model['label'] + ': RAW UNVERIFIED numeric overlap, not accuracy'))
        overlap = [r for r in model.get('rcp_overlap', []) if r['year'] == 2030 and r['threshold_m'] == 1]
        if overlap:
            display(pd.DataFrame([{'scenario': r['scenario'], 'matched': r['matched'], **r['cells']} for r in overlap]))
    '''), md('''
    ## Lab: interpret the off-diagonal cells

    In an invented matched cohort of 100, both methods flag 12 rows, original alone flags 8, Nature alone flags 20, and neither flags 60. How many are matched? Which method is more accurate? What changes if 25 additional cohort rows lack Nature elevations?

    **Worked answer:** The matrix conserves 100 rows. Accuracy is unknown because the labels answer different questions and neither is observed truth. Original flags 20/100 and Nature flags 32/100 in the matched subset. With 25 unmatched rows, coverage is 100/125=80%; the four observed cells do not change. Never silently classify those 25 as “neither.”

    **Deliverable:** A comparison paragraph containing the model/version, fixed threshold, covered and full denominators, paired cohort, datum warning and one additional input needed for a flood assessment (for example local water levels, hydraulic connectivity or defenses).
    ''')]


def lesson17():
    return [md('''
    ## Objectives: test sensitivity without inventing a forecast

    Explore how a hypothetical height offset changes a threshold count. Separate this controlled experiment from a new DEM comparison. Use the local sample interface only if authorized, keeping private outputs out of publication.

    The following 3D surfaces and ten example rows are **entirely fictional**. Their horizontal axes are arbitrary teaching units and their vertical separation is exaggerated. They are not geoid grids, facility observations, real coastlines or evidence about a particular city.
    '''), code('''
    x = np.linspace(-2, 2, 32)
    xx, yy = np.meshgrid(x, x)
    geoid = .15*np.sin(xx)*np.cos(yy)
    sea = geoid + .7 + .1*xx
    ground = 1.3 + .2*xx + .25*np.cos(yy)
    fig = go.Figure()
    for name, surface, color, opacity in [
        ('Fictional geoid', geoid, '#825aa6', .6),
        ('Fictional mean sea surface', sea, '#279fb5', .65),
        ('Fictional terrain', ground, '#b99367', .85)]:
        fig.add_surface(x=xx, y=yy, z=surface, name=name, showscale=False,
                        colorscale=[[0, color], [1, color]], opacity=opacity,
                        hovertemplate=name + '<br>height %{z:.2f} m<extra></extra>')
    show(fig.update_layout(title='FICTIONAL reference surfaces — not a geographic map',
                           scene=dict(xaxis_title='Arbitrary x', yaxis_title='Arbitrary y',
                                      zaxis_title='Height above fictional ellipsoid (m)')))
    display(pd.DataFrame({'surface': ['geoid', 'mean sea', 'terrain'],
                          'height_at_x0_y0_m': [0, .7, 1.55]}))
    '''), md('''
    ## Move the threshold and the hypothetical height shift

    Increasing the threshold includes more valid rows. Increasing the height shift raises terrain relative to a fixed threshold and generally includes fewer. The curve holds the input cohort and missingness fixed. It does not simulate tides, storms, sea-level trajectories, land subsidence, defenses or changing services.

    Input values ≤−7 m and missing cells remain unavailable for every shift. A slider cannot rescue a bad cell. This is a sensitivity experiment on valid values, not a reclassification of source quality.
    '''), code('''
    sensitivity = sensitivity_controls(allow_upload=True)
    demo = fictional_samples()
    base = screening_summary(demo.msl_m, 1, 0)
    raised = screening_summary(demo.msl_m, 1, 1)
    assert base['at_or_below'] == 4 and raised['at_or_below'] == 2
    assert base['available'] == raised['available'] == 8
    print('FICTIONAL worked check: 4 -> 2 when valid heights rise by 1 m; coverage stays 8/10.')
    '''), md('''
    ## Optional private CSV, processed in your browser

    The sampler creates `private-data/nature/samples.csv`. Its required interface is `uid,model,msl_m`; `original_mhhw_m` is optional. Each model has one row per supported facility. Missing heights remain blank, and excluded raw heights retain the ≤−7 rule. The upload reader ignores other columns and never displays identifiers or points. Large workbooks should be converted locally with `scripts/analyze_nature.py` first; rasterio and Excel parsing are not browser dependencies.

    In **JupyterLite**, the explicit upload is read in browser memory. The helper sends no data to an external service and clears the upload widget's raw bytes after processing, including rejected files. Only the parsed dataframe remains in kernel memory for analysis. Saving or downloading an executed notebook can preserve its outputs; keep private-session notebooks local and do not publish them. **Restore fictional demo** clears the upload and replaces the private dataframe with the default fictional example. Reloading JupyterLite ends its browser kernel session. In **local/server Jupyter**, restart or shut down the kernel to clear that kernel's memory; reloading its browser page does not end the server kernel.

    ## Lab: what did the slider prove?

    1. Keep the threshold at 1 m and move the shift from 0 to +1 m. Record the count and coverage.
    2. Restore shift 0 and change the threshold to 10 m. Explain why equality is included.
    3. Write two sentences distinguishing this experiment from comparing CoastalDEM-derived MHHW heights with corrected GLL MSL heights.

    **Worked checks:** The default fixture changes from 4 to 2 at/below 1 m, with coverage fixed at 8/10. At ≤10 m with zero shift, 7 valid rows qualify. Equality follows the declared screening rule. The experiment changes a single numeric input while holding rows fixed; switching DEMs also changes resolution, terrain estimation, acquisition epoch and potentially coverage.

    **Deliverable:** A short methods note and a chart with a fictional/private label, threshold units, coverage, source versions and uncertainty. Explain why neither a low elevation nor a threshold crossing establishes inundation, a return period, lost services or patient impacts. A useful next study would combine validated terrain, consistent water levels and a documented hydrodynamic or connectivity model with separate service-network evidence.
    ''')]


def make_notebook(slug, title, minutes, body):
    cells = [md(f'''
    # {title}

    **Time:** {minutes} minutes · **Prerequisites:** chapters 03–04 or basic Python tables. No private input or GIS installation is required.

    [Run in JupyterLite](https://jltobias.github.io/JupyterLite-Sea-Level-Rise/lite/lab/index.html?path=notebooks/{slug}.ipynb)

    **Reading the book?** It shows saved results. You can zoom and rotate Plotly figures here; Python-backed selectors, sliders and uploads require running the notebook in JupyterLite.

    Wait for **Python (Pyodide) | Idle**, then choose **Run → Run All Cells**. Public results below reflect the bundled aggregate artifact; unavailable models are labeled. Fictional exercises remain explicitly separate from the study.
    '''), code(SETUP), *body, md(SOURCES), code(f"print('Nature lesson complete: {slug}')")]
    return nb.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python (Pyodide)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.13'},
        'coastal_futures': {'estimated_minutes': minutes,
                            'evidence_layers': ['public portfolio aggregates', 'published poster', 'fictional datum demonstrations']}})


def write_notebooks():
    for (slug, title, minutes), body in zip(LESSONS, [lesson14(), lesson15(), lesson16(), lesson17()]):
        nb.write(make_notebook(slug, title, minutes, body), ROOT / 'content/notebooks' / f'{slug}.ipynb')
    return LESSONS


if __name__ == '__main__':
    write_notebooks()
    path = ROOT / 'content/lesson-index.json'
    entries = json.loads(path.read_text(encoding='utf-8'))
    slugs = {s for s, _, _ in LESSONS}
    entries = [e for e in entries if e['slug'] not in slugs]
    entries.extend({'slug': s, 'title': t, 'minutes': m} for s, t, m in LESSONS)
    path.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Authored four Nature lessons; earlier notebooks preserved.')
