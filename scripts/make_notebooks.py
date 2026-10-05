"""Author the executable learning sequence. Edit lesson text here, then regenerate."""
from pathlib import Path
import textwrap
import nbformat as nb

ROOT=Path(__file__).resolve().parents[1]
BASE='https://jltobias.github.io/JupyterLite-Sea-Level-Rise'
POSTER='https://plus.iasociety.org/sites/default/files/2024-09/e-poster_755.pdf'
SETUP='''
# First run downloads Python packages in JupyterLite; subsequent runs use browser caches.
import sys
if sys.platform == 'emscripten':
    import piplite
    await piplite.install(['numpy', 'pandas', 'matplotlib', 'plotly', 'ipywidgets'])
from pathlib import Path
root = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(root))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from IPython.display import display, HTML
from coastlab import (DATA, SCENARIOS, YEARS, COLORS, load_data, select, cards,
                      toy_slr, toy_probability, cumulative_probability,
                      haversine_km, show, dashboard, land_traces)
facilities, exposure = load_data()
published = pd.read_csv(DATA / 'poster_aggregates.csv')
print('Ready: public poster aggregates + clearly labeled fictional facility fixtures.')
'''

def md(s): return nb.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s): return nb.v4.new_code_cell(textwrap.dedent(s).strip())
LESSONS=[]
def lesson(slug,title,minutes,goals,cells):
    intro=f'# {title}\n\n**Time:** {minutes} minutes · **Prerequisites:** basic Python; run cells from top to bottom.\n\n{goals}\n\n[Run this notebook in JupyterLite]({BASE}/lite/lab/index.html?path=notebooks/{slug}.ipynb) · [Full-screen dashboard]({BASE}/dashboard/) · [Official poster]({POSTER})\n\nEach notebook runs independently. Use **Run → Run All Cells**; the first package download can take a minute. Save a downloaded copy to keep your work. The read-only book includes executed examples.'
    n=nb.v4.new_notebook(cells=[md(intro),code(SETUP)]+cells,metadata={'kernelspec':{'display_name':'Python (Pyodide)','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'},'coastal_futures':{'evidence_layers':['published poster','fictional teaching data'],'estimated_minutes':minutes}})
    nb.validate(n)
    path=ROOT/'content/notebooks'/f'{slug}.ipynb';nb.write(n,path)
    LESSONS.append((slug,title,minutes))

lesson('00_start_here','Start here: a coastline, a clinic, a question',20,
'Learn to distinguish hazard, exposure and service disruption; locate the public evidence; run your first browser-based calculation.',[
md(r'''
## The question behind the poster

A clinic may remain above floodwater while roads, electricity, medicine deliveries or referral services fail. A facility count is a useful screening measure, but it cannot tell us how many people lose treatment access. The AIDS 2024 study asks where coastal hazards could intersect the PEPFAR facility portfolio, especially by 2030, and how that exposure could grow through 2100.

![Conceptual comic: storm water threatens a clinic; a flooded road cuts access to a dry clinic; an elevated route and backup services help maintain care.](../assets/continuity-comic.png)

*AI-generated conceptual illustration; fictional places and people. It is not evidence of a real event.*

## Three evidence layers

| Layer | What you can conclude | What you cannot conclude |
|---|---|---|
| Published poster tables | What the authors reported for a specified scope, scenario and year | An individual facility's location or current operational status |
| IPCC reference values | A historical assessment's global sea-level ranges, with a stated baseline | A local clinic's inundation depth |
| Fictional lab | How code, filters and assumptions change a result | Real-world exposure or patient impact |

The interactive dashboard opens on the published evidence. Its separate fictional layer makes it possible to learn facility-level methods without distributing confidential coordinates.
'''),code('''
portfolio = published.query("scope == 'portfolio' and year == 2030")
display(portfolio[['scenario','facilities_2023','potentially_flooded','percent']])
print('The 2023 denominator is a portfolio snapshot, not a forecast of the 2030 health system.')
'''),md(r'''
## Your first investigation

1. Open the dashboard below. Start with RCP 2.6 and 2030.
2. Read the numerator, denominator and percentage aloud.
3. Switch to Published cities, choose Thailand and Bangkok, then move to 2100.
4. Explain why changing reporting scope changes the denominator.
5. Switch to Fictional facility lab. Identify the banner that changes the interpretation.
'''),code("dashboard()"),md(r'''
## Check your understanding

**Prompt:** A point has a modeled annual flood probability of 10%. Does this mean it floods exactly once every ten years? Does it mean 10% of patients lose care?

**Answer:** Neither. Probability describes uncertainty over repeated comparable years under a model. Timing is irregular, and patient outcomes require additional evidence about attendance, access routes, building resilience and alternatives.

**Deliverable:** Write a three-sentence observation using the words *reported*, *scenario* and *denominator*. Keep recommendations separate from observations.

**Facilitator tip:** Pair a public-health learner with a geospatial learner. Ask each to identify one assumption the other might overlook.
''')])

lesson('01_read_the_poster','Read and audit the entire poster',35,
'Trace the background → methods → results → discussion → next steps; reproduce the published tables; identify an internal discrepancy.',[
md(r'''
## From abstract to an evidence chain

**Background.** Coastal hazards may undermine continuity of HIV services, with unequal consequences for communities already facing barriers to care.

**Methods.** The poster describes a PEPFAR site portfolio combined with Climate Central's Portfolio Analysis Tool, CoastalDEM elevation, Kopp et al. sea-level projections and Muis et al. coastal flood modeling. GIS supports spatial comparison, SaTScan supports hotspot investigation, and Power BI presents scenario tabs.

**Results.** Read Tables 1–3 as projections under assumptions, not a list of observed flood events. The reported portfolio denominator is 25,873 supported facilities in 2023. The five published city/district pairs are examples, not the entire portfolio.

**Discussion.** Exposure motivates resilience planning; it does not establish a causal estimate of HIV outcomes. Community participation, continuity of treatment and displacement are central to interpretation.

**Next steps.** The poster proposes linking monitoring indicators to estimate the services potentially affected and supporting adaptation planning. Those indicators are not supplied as public data here.

The lesson covers the final official poster. Power BI's embedded abstract has wording and numeric variants; the source audit records those rather than silently merging versions.
'''),code('''
portfolio = published.query("scope == 'portfolio'")
table = portfolio.pivot(index='year',columns='scenario',values='potentially_flooded')
display(table)
fig = px.line(portfolio,x='year',y='potentially_flooded',color='scenario',markers=True,
              color_discrete_map=COLORS,title='Published Tables 1–3: whole portfolio')
fig.update_layout(yaxis_title='Potentially flooded facilities',xaxis_title='Projection year')
show(fig)
'''),md(r'''
## Recalculate before repeating a claim

The narrative reports approximately 2.8× growth under RCP 2.6 and 3.8× under RCP 8.5 from 2030 to 2100. Calculate the ratios from the tables. An inconsistency is a reason to ask the authors about versions and definitions; it is not permission to alter the source.
'''),code('''
ratio = table.loc[2100] / table.loc[2030]
audit = pd.DataFrame({'table_ratio':ratio, 'narrative_ratio':[2.8,np.nan,3.8]},index=SCENARIOS)
audit['table_percent_increase'] = 100*(audit.table_ratio-1)
display(audit.round(3))
assert table.loc[2030,'RCP 2.6'] == 108
assert table.loc[2100,'RCP 2.6'] == 321
print('RCP 2.6: 321 / 108 ≈ 2.97×, not 2.8×. RCP 8.5: 412 / 108 ≈ 3.81×.')
'''),code('''
# City and district rows are separate reporting units; choose exactly one scope.
bangkok = published.query("city == 'Bangkok' and scenario == 'RCP 2.6'")
display(bangkok.pivot(index='year',columns='scope',values=['potentially_flooded','facilities_2023']))
'''),md(r'''
## Lab: write a defensible result

Calculate the 2030 and 2100 percentage for Bangkok **city** under RCP 8.5, then for its **district** row. Describe why summing those two rows would require geographic overlap information that the poster does not provide.

**Worked check:** City: 13/19 ≈ 68.4% in 2030 and 16/19 ≈ 84.2% in 2100. District: 18/24 = 75% and 21/24 = 87.5%. These small denominators produce much larger percentages than the full portfolio.

**Source-quality note:** Table 1 prints 12/137 as 6.8% in one cell; this repository retains the count and computes 8.8%. It also distinguishes the 2025 95–95–95 targets from the wider 2030 ending-AIDS agenda. Read the [UNAIDS explanation](https://www.unaids.org/en/resources/documents/2024/progress-towards-95-95-95).

**Deliverable:** A 150-word summary with background, method, one numeric result, one limitation and one next step. Cite the official poster and label your ratio as a recalculation from its tables.
''')])

lesson('02_three_rcp_pathways','Three RCP pathways, many possible futures',35,
'Distinguish a forcing pathway from a model; interpret baselines and intervals; compare scenarios without treating them as probabilities.',[
md(r'''
## What the numbers mean

RCP 2.6, RCP 4.5 and RCP 8.5 label representative radiative-forcing pathways, conventionally expressed in W/m² near 2100. They are not degrees of warming, metres of sea-level rise or probabilities. Multiple physical models can be run under the same pathway. RCP 8.5 is a high-forcing scenario, not an assertion that it is the most likely future.

Modern SSP-based assessments add a socioeconomic framework. SSP1-2.6 is not an interchangeable replacement for RCP 2.6: model generation, baselines and assumptions also matter. The book keeps the poster's historical RCP framework and links to [IPCC AR6](https://www.ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/) for context.

## Read a historical assessment carefully

The reference CSV below transcribes six rows of **IPCC AR5 WGI Table SPM.2**: global mean sea-level change relative to **1986–2005**, averaged over **2046–2065** or **2081–2100**. These are period averages, not exact-year local predictions. They are educational context, not inputs used to recreate the poster's PAT calculations.
'''),code('''
ref = pd.read_csv(DATA / 'ipcc_ar5_reference.csv')
display(ref)
late = ref.query("period == '2081-2100'")
fig = go.Figure()
for _,r in late.iterrows():
    fig.add_trace(go.Scatter(x=[r.scenario],y=[r.mean_m],mode='markers',name=r.scenario,
        marker=dict(size=14,color=COLORS[r.scenario]),
        error_y=dict(type='data',symmetric=False,array=[r.likely_high_m-r.mean_m],arrayminus=[r.mean_m-r.likely_low_m])))
fig.update_layout(title='IPCC AR5: global change, 2081–2100 average',yaxis_title='Metres relative to 1986–2005',showlegend=False)
show(fig)
'''),md(r'''
The ranges overlap. A pathway difference is not the only uncertainty: ice dynamics, ocean change, land motion and elevation errors can matter locally. A Bangkok facility cannot be classified by comparing its height to a global average unless the vertical datums, local processes and flood processes are made consistent.

## A deliberately simple teaching curve

For interactive labs we invent a 2020 baseline and endpoints of 0.45, 0.65 and 1.00 m in 2100. With $t=(y-2020)/80$, the curve is $0.2t+(H-0.2)t^2$. These chosen values are **not** the AR5 table, a fitted forecast, Kopp outputs or Climate Central data.
'''),code('''
toy = pd.DataFrame([{'scenario':s,'year':y,'toy_slr_m':toy_slr(s,y)} for s in SCENARIOS for y in YEARS])
fig=px.line(toy,x='year',y='toy_slr_m',color='scenario',markers=True,color_discrete_map=COLORS,
            title='Invented teaching curves — fictional 2020 baseline')
show(fig)
'''),md(r'''
## Lab: compare like with like

Write a function that rejects combining projection tables when their baseline or period differs. Then explain why the near-term ordering in the published poster is 108, 107 and 108 in 2030. Do not force the historical data to be monotonic across scenarios just because the teaching curves are.

**Worked interpretation:** Scenario differences can be small near-term and do not override source-specific uncertainties and processing. The published 107 should remain 107. Explain the difference rather than replacing it with 108.

**Deliverable:** A labeled interval plot and a caption naming the source, vertical unit, baseline and time window.

Reference: [IPCC AR5 WGI Summary for Policymakers, Table SPM.2](https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_SPM_FINAL.pdf).
''')])

lesson('03_probability_and_thresholds','Flood probabilities, frequencies and thresholds',40,
'Separate event rates from probabilities; calculate cumulative exposure; test how a threshold changes a headline count.',[
md(r'''
## Start with the unit

Annual exceedance probability $p$ is bounded by 0 and 1. An expected annual number of events $\lambda$ can exceed 1. The source workbook's EAE fields contain values above 1, so treating them directly as probability fractions is incorrect. Their full definitions, time windows and category rules need the original PAT metadata.

Under an explicitly assumed Poisson process, $P(N\geq1)=1-e^{-\lambda}$. That conversion is a model assumption, not a universal interpretation of an undocumented column.

For independent annual exceedance indicators with probabilities $p_y$, the probability of at least one event is $1-\prod_y(1-p_y)$. Independence may be unrealistic, and a changing climate makes constant annual probabilities a weak long-term assumption. A return period $T=1/p$ is an average recurrence concept under stationarity, not a timetable.
'''),code('''
p = 0.10
display(pd.DataFrame({'years':[1,10,30], 'at_least_one':[cumulative_probability([p]*n) for n in [1,10,30]]}))
rates=np.array([.01,.1,1,12])
display(pd.DataFrame({'assumed_Poisson_events_per_year':rates,'probability_at_least_one':1-np.exp(-rates)}))
assert np.isclose(cumulative_probability([.1]*10),1-.9**10)
'''),md(r'''
## A classification is a decision rule

The fictional lab uses a logistic response: $p=1/(1+\exp((e-s-u)/a))$, with invented elevation $e$, sea-level increment $s$, surge offset $u=0.7$ m and scale $a=0.55$ m. This helps reveal how small height changes can affect a threshold. It has no calibration to the real portfolio.

The slider classifies a site as exposed when $p\geq\tau$. Changing $\tau$ changes the count even though the underlying probabilities have not changed. The denominator remains all facilities in the selected cohort.
'''),code('''
rows=select(facilities,exposure,scenario='RCP 8.5',year=2100)
thresholds=np.linspace(.01,.99,99)
fig=go.Figure(go.Scatter(x=thresholds,y=[cards(rows,t)['above_threshold'] for t in thresholds],mode='lines'))
fig.update_layout(title='Fictional count is sensitive to the decision threshold',xaxis_title='Annual probability threshold',yaxis_title='Facilities above threshold')
show(fig)
print('Sum of marginal probabilities (expected exposed facilities):',round(rows.annual_probability.sum(),2))
print('Threshold count:',cards(rows,.1)['above_threshold'])
'''),code('''
# Annual interpolation is explicit; nine decadal values are NOT nine decades of annual data.
example = exposure.query("facility_id == 'DEMO-01-001' and scenario == 'RCP 8.5'").sort_values('year')
annual_years=np.arange(2030,2061)
annual_p=np.interp(annual_years,example.year,example.annual_probability)
print('Illustrative 2030–2060 cumulative probability, independent years:',cumulative_probability(annual_p))
'''),md(r'''
## Lab: interrogate uncertainty

Change the surge offset by ±0.25 m and compare counts at thresholds 1%, 10% and 50%. Then describe which is uncertainty about nature and which is a decision-maker's threshold.

**Worked check:** At fixed probabilities, increasing the threshold cannot increase the number classified as exposed. The sum of marginal probabilities is an expected number of exposed sites; it does not require independence between sites. Cumulative probability across years does require a dependence assumption for the product formula.

**Deliverable:** A sensitivity table with units and a paragraph stating the independence assumption. Do not add probabilities across years or interpret modeled exposed sites as affected patients.
''')])

lesson('04_data_and_geography','From spreadsheets to defensible maps',45,
'Reshape wide Power BI fields into a tidy panel; validate joins; explain why map scale, coordinate systems and privacy matter.',[
md(r'''
## Inspect the grain before the map

The Power BI model is wide: A/B/C columns encode RCP 2.6/4.5/8.5 and suffixes 20–90 and 00 encode decades 2020–2090 and 2100. The confirmed tab titles establish the scenario mapping. Names such as R26EAE400 and R65EAE50 need explicit review rather than silent renaming.

Our fictional panel uses one row per **facility × scenario × year**. Facility attributes live in a separate dimension table. Never sum the dimension's service load across all scenario-year rows: each facility would be repeated 27 times.
'''),code('''
display(facilities.head(3))
display(exposure.head(6))
joined=facilities.merge(exposure,on='facility_id',validate='one_to_many')
print('Facilities:',len(facilities),'Panel rows:',len(joined))
print('Naive repeated sum / true service-load sum:',joined.service_load.sum()/facilities.service_load.sum())
assert len(joined)==len(facilities)*3*9
'''),code('''
# Demonstrate a wide-to-long conversion using FICTIONAL category columns.
wide=pd.DataFrame({'facility_id':['DEMO-X','DEMO-Y'],'A30':['YELLOW','NOFILL'],'B30':['ORANGE','NOFILL'],'C00':['RED','YELLOW']})
long=wide.melt(id_vars='facility_id',var_name='source_field',value_name='source_category')
long['scenario']=long.source_field.str[0].map({'A':'RCP 2.6','B':'RCP 4.5','C':'RCP 8.5'})
long['year']=long.source_field.str[1:].map(lambda suffix:2100 if suffix=='00' else 2000+int(suffix))
display(long)
'''),md(r'''
## Coordinates are not interchangeable measurements

Longitude/latitude in EPSG:4326 are angular coordinates. Distances in degrees are not distances in metres. A vertical datum is a different concept again: elevation relative to MHHW cannot be mixed casually with ellipsoidal or orthometric elevation.

Natural Earth's 1:110 million land outlines are sufficient for a global orientation map. They do not resolve local drainage, seawalls or a building footprint. The map below plots **invented** points; points in water or implausible locations are expected because they are random teaching fixtures, not a land-filtered facility inventory.
'''),code('''
rows=select(facilities,exposure,country='Thailand',year=2030)
fig=go.Figure(land_traces())
fig.add_trace(go.Scatter(x=rows.longitude,y=rows.latitude,mode='markers',text=rows.facility_id,
    marker=dict(size=9,color=rows.annual_probability,cmin=0,cmax=1,colorscale='YlOrRd'),name='Fictional sites'))
fig.update_layout(title='Fictional Thai-city examples; coarse coastline for context',xaxis=dict(title='Longitude',range=[99,102]),yaxis=dict(title='Latitude',range=[12,15]))
show(fig)
a,b=rows.iloc[0],rows.iloc[1]
print('Great-circle distance, not road travel distance (km):',round(haversine_km(a.longitude,a.latitude,b.longitude,b.latitude),2))
'''),md(r'''
## Lab: catch a misleading join

Duplicate a facility identifier in the dimension table and try a `validate='one_to_many'` merge. Catch the resulting error, then explain why removing duplicates without knowing which record is authoritative is also unsafe.

**Worked check:** A valid panel has 192 unique fictional facilities, 3 scenarios, 9 years and 5,184 rows. Selecting one year and one scenario returns at most 192 rows. A city filter changes the cohort before aggregation.

**Privacy checkpoint:** Removing names does not anonymize precise coordinates. This public repository contains only poster aggregates and independently generated fictional facility data. A private audit workflow should stay in an approved environment and should never commit raw workbooks or UID-coordinate pairs.

**Deliverable:** A one-page data contract specifying grain, join keys, coordinate reference system, missing-value treatment and allowed publication level. Consult the book's data dictionary and Power BI crosswalk.
''')])

lesson('05_dashboard_lab','Power BI ideas in a browser: slicers, cards and listings',45,
'Use all three scenario tabs; audit filter propagation; build a small Python widget dashboard and compare it with the full browser dashboard.',[
md(r'''
## A dashboard is a set of coordinated questions

The original report contains maps, country/city/PEPFAR slicers, decade classifications, tables, treemaps and cards. This browser implementation retains the scenario tabs, geographic slicers, year animation, line listings and aggregates. The public layer works at the poster's published reporting units; the fictional layer demonstrates facility-level inspection and service filters.

**Filter contract:** scenario and year define the current slice. Country and city select a cohort. Public scope chooses exactly one of city, district or whole portfolio. A fictional threshold changes the numerator; it does not remove facilities from the denominator. Listing search is deliberately local to the table and its label says so. Time-series charts retain the cohort while showing all years and all three scenarios.
'''),code("dashboard(scenario='RCP 4.5')"),md(r'''
## Build the underlying calculation yourself

The next cell uses `ipywidgets` in JupyterLite. It needs the Python kernel, while the full dashboard above uses browser JavaScript and works without a kernel. The snapshot below is executed in the static book; use the live notebook to change Python widgets.
'''),code('''
import ipywidgets as widgets
scenario_widget=widgets.Dropdown(options=SCENARIOS,description='Scenario:')
year_widget=widgets.SelectionSlider(options=YEARS,value=2030,description='Year:')
country_widget=widgets.Dropdown(options=['All']+sorted(facilities.country.unique()),description='Country:')
threshold_widget=widgets.FloatSlider(min=.01,max=.99,step=.01,value=.1,description='Threshold:')
def update(scenario,year,country,threshold):
    rows=select(facilities,exposure,scenario= scenario,year=year,country=country)
    result=cards(rows,threshold)
    display(pd.DataFrame([result]).round(2))
    display(rows[['facility_id','city','annual_probability']].head(5))
output=widgets.interactive_output(update,{'scenario':scenario_widget,'year':year_widget,'country':country_widget,'threshold':threshold_widget})
display(widgets.VBox([scenario_widget,year_widget,country_widget,threshold_widget,output]))
'''),code('''
# Independently reconcile the card's numerator with its row-level predicate.
rows=select(facilities,exposure,scenario='RCP 4.5',year=2050,country='Thailand')
manual_count=int((rows.annual_probability>=.1).sum())
assert cards(rows)['above_threshold']==manual_count
print('Reconciled:',manual_count,'fictional exposed facilities of',len(rows))
'''),md(r'''
## Lab: audit, do not just explore

1. In the public dashboard, verify portfolio cards for 2030: 108, 107 and 108 for RCP 2.6, 4.5 and 8.5.
2. Move to 2100 and verify 321, 331 and 412.
3. Choose Published cities → Thailand → Bangkok and reconcile the listing with the cards.
4. Reset filters. Switch to the fictional layer and set the same cohort as the Python example.
5. Export a CSV. Count unique IDs and confirm that each ID appears once. Explain why the service-load card is a workload proxy, not a patient count.
6. Raise the threshold. The exposed count should stay the same or decrease; the cohort denominator should stay constant.

**Deliverable:** A screenshot with a short caption naming all active filters, plus an exported CSV and a three-line reconciliation calculation. The static site includes keyboard-accessible controls and a numeric table so colour is never the only way to read a result.
''')])

lesson('06_time_series_maps','Watch the decades: animated maps and temporal comparisons',40,
'Build an animated map of the published aggregates; keep scales fixed; choose between animation and small multiples.',[
md(r'''
## Time is a dimension, not a slide transition

An animation can reveal the sequence of change, but it taxes memory: a reader must remember an earlier frame. Fixed-scale small multiples support direct comparisons. Keep the same locations, denominator, marker-size rule and colour scale across frames.

This map uses five **city** rows from the poster, not district rows or all portfolio sites. The 2023 denominator is held fixed, as in the source tables. The time steps are modeled decades; the animation does not imply that exposure changes only once each decade.
'''),code('''
city=published.query("scope == 'city' and scenario == 'RCP 8.5'").copy()
fig=px.scatter(city,x='longitude',y='latitude',animation_frame='year',animation_group='city',
    size='potentially_flooded',size_max=45,color='percent',range_color=[0,100],
    hover_name='city',hover_data=['facilities_2023','potentially_flooded'],
    range_x=[-15,120],range_y=[-12,25],color_continuous_scale='YlOrRd',
    title='Published RCP 8.5 city counts, 2030–2100')
for trace in land_traces(): fig.add_trace(trace)
fig.update_layout(xaxis_title='Longitude (°)',yaxis_title='Latitude (°)')
show(fig)
'''),code('''
fig,ax=plt.subplots(figsize=(9,4))
for city_name,g in city.groupby('city'):
    ax.plot(g.year,g.percent,marker='o',label=city_name)
ax.set(xlabel='Projection year',ylabel='Potentially flooded (%)',ylim=(0,100),title='Same evidence, easier decade comparison')
ax.legend(bbox_to_anchor=(1.01,1),loc='upper left');fig.tight_layout();plt.show()
'''),md(r'''
## A short narrated-by-captions visual

This locally bundled video is generated from the same fictional teaching function used in the labs. It shows all three curves and a moving year marker. It contains no observed flood footage and no audio. Captions and the adjacent transcript provide the explanation.

<video controls preload="metadata" style="width:100%" poster="../../assets/teaching-video-poster.png"><source src="../../assets/scenario-walkthrough.mp4" type="video/mp4"><track kind="captions" src="../../assets/scenario-walkthrough.vtt" srclang="en" label="English" default></video>

**Transcript:** The three curves use an invented 2020 baseline. Near-term trajectories are similar by construction. Later differences grow under the chosen endpoints. These are teaching curves, not a climate projection product. Exposure also depends on elevation, storm conditions, access and the definition of risk.
'''),md(r'''
## Lab: choose an honest visual encoding

Create a 2 × 4 small-multiple plot for the eight published decades. Use city names on the horizontal axis and a fixed 0–100% vertical scale. Compare it with the animated map.

**Worked interpretation:** In the RCP 8.5 published city rows, Ho Chi Minh City rises from 0 in 2030 to 28/44 in 2100. Bangkok begins with a high share. A zero in the Mombasa row is a result under the study's definition and inputs; it does not mean the city has no climate hazards.

**Deliverable:** Pick the visual that best answers “which city's percentage changes most?” and justify it. Use animation to explain sequence; use a chart or table to support precise comparisons. External contextual videos listed in the references retain their owners' rights and are linked, not downloaded.
''')])

lesson('07_three_dimensions','3D coasts: useful depth, dangerous certainty',40,
'Build a transparent terrain-and-water scene; distinguish elevation from geographic stems; explore sensitivity without implying hydrodynamic realism.',[
md(r'''
## What does height represent?

A three-dimensional display can encode physical elevation, a statistical value or time. Those meanings are not interchangeable. A map with stems whose height is the percentage of exposed facilities is a geographic chart, not a digital elevation model. A space–time cube uses its vertical axis for time.

The fictional terrain below is an analytic surface over a 4 × 4 km square. It is independent of the city fixtures and has no real coordinate reference system. The water plane is a threshold illustration. It does not simulate water flowing around barriers, wave overtopping, tides, drainage or river flooding.
'''),code('''
x=np.linspace(0,4,51);y=np.linspace(0,4,51)
X,Y=np.meshgrid(x,y)
terrain=.15+.48*X+.16*np.sin(2*X+Y)+.08*np.cos(3*Y)
water=.7+toy_slr('RCP 8.5',2100)
fig=go.Figure([go.Surface(x=x,y=y,z=terrain,colorscale='Earth',showscale=False,name='Invented terrain'),
              go.Surface(x=x,y=y,z=np.full_like(terrain,water),opacity=.55,colorscale=[[0,'#229bd1'],[1,'#229bd1']],showscale=False)])
fig.update_layout(title='Independent fictional coast — exaggerated vertical scale',
    scene=dict(xaxis_title='x (km)',yaxis_title='y (km)',zaxis_title='Toy height (m)',aspectratio=dict(x=1,y=1,z=.6)))
show(fig)
'''),code('''
levels=np.arange(.25,2.01,.25)
sensitivity=pd.DataFrame({'water_m':levels,'cells_below_plane_percent':[100*np.mean(terrain<=level) for level in levels]})
display(sensitivity)
print('This is the share of sampled grid cells below a plane, not a validated inundated area.')
'''),code("dashboard(view='terrain',dataset='synthetic')"),md(r'''
## Lab: make the missing physics visible

Add an elevated ridge to the surface. Compare a simple below-water mask to a connected-ocean mask using a flood-fill starting from the left edge. The second mask should exclude isolated inland depressions until a connected path exists. Neither method supplies a full hydrodynamic model.

**Worked approach:** Use a queue; initialize ocean-edge cells below the water level; visit adjacent below-water cells until no new cells remain. Keep cell resolution fixed. Quantify the difference between all low cells and connected low cells.

**Deliverable:** Two labelled masks and a 3D scene with an explicit vertical-exaggeration note. List the data needed for a real analysis: surveyed heights, datum transformation, local coastal water levels, defences, connectivity and validation events.

Source context: [CoastalDEM v2.1](https://www.climatecentral.org/coastaldem-v2.1). No CoastalDEM raster is distributed or simulated by this surface.
''')])

lesson('08_space_time_cube','Space–time cubes and cohort histories',35,
'Construct a space–time cube from public aggregates; trace a city history; compare a cube with a heatmap.',[
md(r'''
## Stack maps, not populations

Imagine each decade's map as a sheet of paper and stack the sheets in time order. Longitude and latitude locate a city; vertical position locates a year. Colour shows the published potentially flooded percentage. Repeated points are observations of the same reporting unit under different modeled years; they are not additional facilities.

Rotation can reveal patterns but also hide points. Offer a flat alternative with exact values. Keep the colour scale fixed across RCPs.
'''),code('''
city=published.query("scope == 'city' and scenario == 'RCP 8.5'")
fig=go.Figure()
for name,g in city.groupby('city'):
    fig.add_trace(go.Scatter3d(x=g.longitude,y=g.latitude,z=g.year,mode='lines+markers',name=name,
        marker=dict(size=7,color=g.percent,cmin=0,cmax=100,colorscale='YlOrRd'),
        text=[f'{name}: {n} / {d}' for n,d in zip(g.potentially_flooded,g.facilities_2023)],
        hovertemplate='%{text}<br>Year %{z}<extra></extra>'))
fig.update_layout(title='Public city time histories — vertical axis = year',scene=dict(xaxis_title='Longitude',yaxis_title='Latitude',zaxis_title='Year'))
show(fig)
'''),code('''
matrix=city.pivot(index='city',columns='year',values='percent')
fig=px.imshow(matrix,zmin=0,zmax=100,text_auto='.1f',aspect='auto',color_continuous_scale='YlOrRd',
    labels={'color':'Potentially flooded (%)'},title='The same cube unfolded into a heatmap')
show(fig)
'''),md(r'''
## Lab: first crossing is not a predicted event date

Find the first sampled decade in which each city reaches 50% potentially flooded under each RCP. Return “not reached in sampled years” when appropriate. This is a threshold crossing in a modeled series, not the date of a real flood, and the ten-year sampling limits temporal precision.
'''),code('''
city_rows=published.query("scope == 'city'")
crossings=city_rows[city_rows.percent>=50].groupby(['scenario','city']).year.min()
all_keys=pd.MultiIndex.from_product([SCENARIOS,sorted(city_rows.city.unique())],names=['scenario','city'])
display(crossings.reindex(all_keys).rename('first_sampled_year_at_50_percent').to_frame())
'''),md(r'''
**Worked check:** Bangkok's city row is already above 50% in 2030. Abidjan's city row first exceeds 50% in 2070. A missing value means the threshold is not reached in the available series; it should not become zero or 2020.

**Deliverable:** The cube, a heatmap and a one-sentence comparison of the questions each answers best. Avoid interpolating an exact transition date unless you state and defend an interpolation model.
''')])

lesson('09_hotspots','Hotspots: exposure rates and a spatial scan experiment',50,
'Separate count from rate; implement a small maximum-statistic permutation test; explain why it is not a reproduction of SaTScan.',[
md(r'''
## A cluster requires a denominator and a null model

The poster used SaTScan to examine concentrations of potentially flooded facilities. A large exposed count may simply reflect many facilities. A statistical scan compares an inside-window exposure rate with an outside rate under a specified model, then accounts for examining many windows.

Here we build a small **fictional Bernoulli scan experiment** over predefined geographic circles. This is not SaTScan, does not recreate its Gini selection, and does not reproduce the poster's cluster ranks, radii or p-values. Real replication needs the original case/control definitions, windows, maximum population fraction, projection, simulation settings and parameter files.

Reference: [Kulldorff, spatial scan statistic and SaTScan technical documentation](https://www.satscan.org/techdoc.html).
'''),code('''
rows=select(facilities,exposure,scenario='RCP 8.5',year=2100).reset_index(drop=True)
cases=(rows.annual_probability>=.5).to_numpy().astype(int)
windows=[];names=[]
for city,g in rows.groupby('city'):
    lon,lat=g.longitude.mean(),g.latitude.mean()
    distance=np.array([haversine_km(lon,lat,r.longitude,r.latitude) for r in rows.itertuples()])
    for radius in [8,16,24]:
        mask=distance<=radius
        if 0<mask.sum()<len(rows): windows.append(mask);names.append(f'{city}: {radius} km')
windows=np.array(windows)
def log_likelihood(k,n):
    p=np.clip(k/n,1e-12,1-1e-12)
    return k*np.log(p)+(n-k)*np.log1p(-p)
def scan_statistics(labels):
    n=windows.sum(axis=1); k=windows@labels; N=len(labels);K=labels.sum()
    llr=log_likelihood(k,n)+log_likelihood(K-k,N-n)-log_likelihood(K,N)
    return np.where(k/n>(K-k)/(N-n),np.maximum(0,llr),0)
observed=scan_statistics(cases)
winner=int(observed.argmax())
print('Highest-scoring fictional window:',names[winner], 'LLR:',round(observed[winner],3))
'''),code('''
# The null holds the total number of cases fixed and permutes their locations.
rng=np.random.default_rng(2024)
null_max=np.array([scan_statistics(rng.permutation(cases)).max() for _ in range(199)])
p_global=(1+np.sum(null_max>=observed.max()))/(1+len(null_max))
fig,ax=plt.subplots(figsize=(8,4))
ax.hist(null_max,bins=20,color='#087e8b',alpha=.8)
ax.axvline(observed.max(),color='#cb4260',label='Observed maximum')
ax.set(xlabel='Maximum LLR across candidate windows',ylabel='Permutation count',title='Fictional scan: a maximum-statistic null distribution');ax.legend();plt.show()
print('Monte Carlo p-value for strongest tested window:',p_global)
'''),md(r'''
## What the test does and does not say

The maximum statistic adjusts this experiment for the set of circles actually searched. It does not fix a poorly chosen null model or unmeasured spatial differences. Exchangeability assumes that shuffling labels is meaningful; unequal topography and shared exposure mechanisms can violate that assumption. The synthetic probabilities and their threshold are inputs, not observed disease cases.

## Lab

Repeat with 999 permutations and thresholds 0.25 and 0.75. Record the top window, global Monte Carlo p-value and case count. Keep the random seed for reproducibility. Explain why a p-value of zero is inappropriate with a finite permutation sample and why the +1 correction matters.

**Worked check:** With 199 simulations the minimum possible corrected p-value is 1/200 = 0.005. Adding candidate windows changes the maximum-statistic null distribution and must be reflected in the test.

**Deliverable:** A short methods paragraph stating the null model, candidate windows, threshold, seed and simulation count, followed by a limitation explaining why this cannot validate the poster's original clusters.
''')])

lesson('10_continuity_and_equity','From exposed facilities to continuity of care',45,
'Connect coastal exposure to a service network; compute a transparent capacity scenario; explain why patient impacts cannot be inferred from counts alone.',[
md(r'''
## Follow the service, not only the building

The poster's next steps call for connecting facility exposure with program indicators. That linkage requires approved data, compatible periods and clear definitions. An annual service count can include repeated visits by the same person. A headcount, a visit count and a treatment-current indicator cannot be substituted for one another.

For this lab, service loads and spare capacities are hypothetical. We model a small network to reason about continuity: a clinic may be dry but unreachable; an alternative site may be reachable but lack staff, medicines or capacity. Decisions need community knowledge about transport costs, stigma, disability access and displacement.

The original study sits in PEPFAR's historical 2022 strategy context. This lesson teaches a planning method, not a statement about current funding, eligibility or clinical care.
'''),code('''
# Entirely fictional: annual visit capacity, not patients or real PEPFAR indicators.
network=pd.DataFrame({'site':['Coastal A','Coastal B','Inland C','Inland D'],
    'x':[0,1,3,4],'y':[0,2,1,3],'visit_load':[1000,800,1200,600],
    'spare_capacity':[0,0,500,400],'unavailable':[True,True,False,False]})
edges=[(0,2),(0,3),(1,2),(1,3),(2,3)]
fig=go.Figure()
for a,b in edges:
    fig.add_trace(go.Scatter(x=network.loc[[a,b],'x'],y=network.loc[[a,b],'y'],mode='lines',line=dict(color='#a0b5bb'),showlegend=False,hoverinfo='skip'))
fig.add_trace(go.Scatter(x=network.x,y=network.y,mode='markers+text',text=network.site,textposition='top center',
    marker=dict(size=network.visit_load/40,color=['#cb4260' if x else '#087e8b' for x in network.unavailable]),showlegend=False))
fig.update_layout(title='Fictional referral graph — schematic, not a road map',xaxis=dict(visible=False),yaxis=dict(visible=False))
show(fig)
'''),code('''
disrupted=network.loc[network.unavailable,'visit_load'].sum()
spare=network.loc[~network.unavailable,'spare_capacity'].sum()
reroutable=min(disrupted,spare)
print({'hypothetical_disrupted_annual_visits':int(disrupted),'capacity_only_upper_bound_rerouted':int(reroutable),
       'remaining_visit_capacity_gap':int(disrupted-reroutable)})
# Capacity-only bound assumes all alternative routes and services are usable.
assert disrupted-reroutable == 900
'''),code('''
alternatives=pd.DataFrame({'option':['Backup power','Access-route improvement','Mobile service','Referral capacity'],
    'illustrative_cost_units':[2,5,3,4],'illustrative_visits_restored':[200,500,350,500]})
alternatives['visits_per_cost_unit']=alternatives.illustrative_visits_restored/alternatives.illustrative_cost_units
display(alternatives)
'''),md(r'''
## Lab: challenge the ranking

Add an equity criterion and a time-to-implement criterion to the options table. Explain why maximizing visits per cost alone could disadvantage remote communities. Avoid inventing precise weights and presenting the outcome as an objective optimum.

**Worked discussion:** The 900-visit gap is a capacity accounting exercise under assumptions, not an estimate of people missing treatment. The graph omits travel times and its edges may fail together. The option impacts may overlap, so adding their benefits could double-count restored services.

**Deliverable:** A scenario memo with an exposure statement, an access constraint, two feasible responses, a stakeholder consultation plan and a monitoring trigger. Keep risk assessment, value judgments and resource choices visible.

Reference: [PEPFAR's 2022 strategic direction](https://www.state.gov/wp-content/uploads/2022/09/PEPFAR-Strategic-Direction_FINAL.pdf); [UNAIDS explanation of cascade denominators](https://www.unaids.org/en/resources/documents/2024/progress-towards-95-95-95).
''')])

lesson('11_capstone','Capstone: a coastal continuity briefing',60,
'Produce a reproducible public-results briefing and a separate fictional adaptation experiment, with a clear evidence boundary.',[
md(r'''
## Your commission

A country planning team needs a five-minute briefing on what the AIDS 2024 poster can and cannot tell them. Select one of the five published city groups. Compare RCP 2.6, 4.5 and 8.5 from 2030 to 2100. Then use fictional data to demonstrate a possible decision-support workflow. Never attach the fictional outputs to a real facility or call them updated study results.

## Required products

1. A one-paragraph abstract covering context, method, finding, limitation and next step.
2. A map and a three-scenario line chart using one reporting scope and fixed scales.
3. A line listing whose counts reconcile with a card summary.
4. An uncertainty or threshold experiment using fictional data.
5. A continuity-of-care diagram and two adaptation choices for stakeholder discussion.
6. Source citations, a data dictionary excerpt, license notices and a methods log.
'''),code('''
chosen_city='Bangkok'   # Edit this and rerun.
chosen_scope='city'    # Choose city OR district, never sum them.
brief=published[(published.city==chosen_city)&(published.scope==chosen_scope)].copy()
display(brief[['scenario','year','facilities_2023','potentially_flooded','percent']])
fig=px.line(brief,x='year',y='percent',color='scenario',markers=True,color_discrete_map=COLORS,
            title=f'Published {chosen_city} ({chosen_scope}): three pathways')
fig.update_yaxes(range=[0,100],title='Potentially flooded facilities (%)')
show(fig)
'''),code('''
endpoint=brief[brief.year.isin([2030,2100])].pivot(index='scenario',columns='year',values='potentially_flooded')
endpoint['absolute_change']=endpoint[2100]-endpoint[2030]
endpoint['ratio']=endpoint[2100].div(endpoint[2030].replace(0,np.nan))
display(endpoint)
print('When the baseline is zero, a ratio is undefined; report absolute change instead.')
'''),code('''
# Export your public aggregate briefing table in the notebook file browser.
output=Path('my_public_briefing.csv')
brief.to_csv(output,index=False)
print('Saved',output,'— download it from JupyterLite to retain your work.')
'''),md(r'''
## Peer-review rubric (20 points)

| Criterion | Points | Evidence |
|---|---:|---|
| Correct evidence layer and reporting scope | 4 | Public and fictional results clearly separated |
| Reproducible numbers | 4 | Numerator, denominator, years and filters reconcile |
| Visual integrity | 4 | Units, fixed scales, accessible labels, appropriate map scale |
| Scientific interpretation | 4 | RCPs, uncertainty and exposure-vs-impact distinguished |
| Attribution and actionability | 4 | Sources, rights, limitations and community-informed next step |

**Worked answer fragment:** “In the published Bangkok city row, RCP 8.5 increases from 13 of 19 facilities in 2030 to 16 of 19 in 2100. These are projected exposure classifications in a fixed portfolio snapshot. They do not measure service interruptions or patient outcomes.”

**Stretch task:** Replace the invented exposure function with an approved public projection dataset. Record its version, license, vertical datum, baseline, scenario definitions and validation procedure before generating any new map. Update the schema tests and keep the historical poster results intact.

**Submission:** Download the notebook, CSV and figures. JupyterLite stores edits in your browser; it does not commit them to GitHub automatically.
''')])

lesson('12_reproduce_and_extend','Reproduce, audit and extend the study responsibly',40,
'Understand what has been verified; locate missing replication inputs; design an approved-data workflow without exposing private records.',[
md(r'''
## What this repository reproduces

The 264-row public table reproduces the counts printed in the poster's three tables: three scenarios × eight decades × eleven reporting rows. It supports recalculated percentages and ratios and new visualizations of that public evidence. The whole-portfolio totals were also checked locally against the supplied workbook's PEPFARSUP = 1 records and non-NOFILL decade categories.

This does **not** reproduce the original elevation processing, PAT flood model or SaTScan analysis. The PBIX and PBIP were inspected for schema and visual design; raw records and confidential coordinates are excluded. A separate local audit script accepts a user-provided workbook and prints only comparisons against already-public portfolio totals.

## The methods chain and its dependencies

| Step | Inputs needed for scientific replication | Public teaching substitute |
|---|---|---|
| Facility portfolio | Approved UID/location snapshot, support definition, quality checks | Poster counts; fictional facility dimension |
| Elevation assignment | DEM version, horizontal/vertical datums, interpolation and effective-elevation definition | Analytic fictional terrain |
| Coastal water levels | Local projection distributions, surge/tide product, model settings | Explicit toy curve and logistic probability |
| Classification | Complete PAT field and colour-category metadata | Transparent adjustable threshold |
| Spatial scan | SaTScan parameter file, case/control tables, window limits and Monte Carlo seed | Small documented permutation experiment |
| Program impact | Approved indicators and linkage/aggregation rules | Hypothetical service loads and capacity |
'''),code('''
from coastlab import validate
validate(facilities,exposure)
assert len(published)==3*8*11
assert not published.duplicated(['scenario','year','city','scope']).any()
assert published.potentially_flooded.between(0,published.facilities_2023).all()
print('Public aggregate keys, counts and fictional-panel contracts pass.')
'''),md(r'''
## Original-field crosswalk

`A30`, `B30`, `C30` identify scenario classifications for 2030; `A00`, `B00`, `C00` represent 2100. `ACTUALE` is renamed `ACTUAL_MHHW_ELEV_M` in the model. `CNTRYNAME`, `CITYNAMESJ`, `PEPFARSUP` and `uid` support filtering and identification. `TXCURR23` suggests a program indicator but its definition and release rights require confirmation. Numeric EAE/ECE fields cannot be treated as probabilities merely because they concern exceedance.

The source includes anomalous spellings and mixed integer/decimal typing in scenario metrics. Preserve original names in an ingestion record; use reviewed aliases only when their intended meaning is confirmed. Never create an RCP 6.5 scenario from an apparent R65 field typo.

## Lab: an approved-data ingestion plan

Describe how you would validate unique identifiers, coordinate ranges, vertical datum, missingness, scenario-year completeness and joins. State which outputs may be published and what disclosure review is needed for small-area groups. Data possession alone is not a redistribution license.

**Worked check:** If you refresh the portfolio, changes in exposure counts may reflect a changing denominator as well as climate. A fixed-cohort comparison and a contemporary-portfolio comparison answer different questions; report both explicitly if both are used.

**Deliverable:** A reproducibility manifest with input hashes, source versions, license/access conditions, settings, software versions and output checks. The bundled `provenance.json`, source audit and data dictionary provide a starting point.
''')])

from powerbi_lesson import write_notebook as write_powerbi_notebook
LESSONS.append(write_powerbi_notebook())
(ROOT/'content/lesson-index.json').write_text(__import__('json').dumps([{'slug':s,'title':t,'minutes':m} for s,t,m in LESSONS],indent=2),encoding='utf-8')
print(f'Authored {len(LESSONS)} notebooks.')
