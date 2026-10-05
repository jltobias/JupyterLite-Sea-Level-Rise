# Data dictionary and Power BI crosswalk

## Published aggregates: `poster_aggregates.csv` / `poster-aggregates.json`

264 rows; unique key **scenario + year + city + scope**. Counts transcribed manually from the official poster; whole-portfolio totals cross-checked locally against the supplied workbook. Percentages are recalculated. No facility locations are present.

| Field | Type / unit | Definition and constraints |
|---|---|---|
| scenario | string | RCP 2.6, RCP 4.5 or RCP 8.5 |
| year | integer / year | 2030–2100 inclusive, decade steps; no published 2020 table row |
| country | string | Country of named city; `All` for portfolio |
| city | string | Abidjan, Bangkok, Ho Chi Minh City, Lagos, Mombasa or All PEPFAR |
| scope | enum | `city`, `district`, `portfolio`; never sum scopes together |
| facilities_2023 | integer / facilities | Fixed supported-facility denominator printed in the 2023 column |
| potentially_flooded | integer / facilities | Printed count for the scenario/year; not an observation of flooding |
| percent | float / percent | 100 × potentially_flooded / facilities_2023; recomputed, not the poster's rounded text |
| longitude | float / degrees east | Manually chosen approximate city anchor for contextual display; blank for portfolio |
| latitude | float / degrees north | Same convention; not a facility coordinate or a district centroid |
| source_table | integer | Table 1, 2 or 3 in the official poster |

The five city groups do not sum to All PEPFAR. District footprints and overlap with city rows are not supplied. Country filters cover only the published examples, not a complete national portfolio. Missing coordinates for the portfolio row are intentional, not zero.

## Fictional facilities: `synthetic_facilities.csv`

192 rows; unique key **facility_id**. Generated with Python's seeded standard-library random generator (`20240722`), never read from or jittered around real facility records. Twenty-four examples per manually chosen city anchor. EPSG:4326 display coordinates; not land-masked.

| Field | Type / unit | Definition |
|---|---|---|
| facility_id | string | `DEMO-cc-nnn`; never a DATIM UID |
| name | string | Explicitly fictional clinic name |
| country, city | strings | Contextual geography labels, not claims about PEPFAR's current footprint |
| longitude, latitude | floats / degrees | Invented offsets around approximate city anchors; may fall on water |
| elevation_m | float / m | Invented height above a fictional local reference; not MHHW or a sampled DEM |
| service_load | integer / annual visits | Hypothetical annual appointment workload; not patients or TX_CURR |
| service_type | enum | Primary care, HIV services, Referral; fictional categories |
| pepfar_demo | integer / boolean | 0/1 hypothetical support flag for slicer teaching; not observed support |
| is_synthetic | integer / boolean | Always 1 |

## Fictional panel: `synthetic_exposure.csv`

5,184 rows; unique key **facility_id + scenario + year**. Complete 192 × 3 × 9 panel. Foreign key to the fictional facility table.

| Field | Type / unit | Definition |
|---|---|---|
| facility_id | string | Reference to fictional facility |
| scenario | enum | RCP labels used to compare chosen teaching trajectories |
| year | integer | 2020–2100 in ten-year steps |
| toy_slr_m | float / m | Invented quadratic trajectory relative to fictional 2020 baseline |
| annual_probability | float / fraction | Invented logistic output in [0,1]; no calibration to PAT |
| is_synthetic | integer | Always 1 |

With `t=(year-2020)/80`, `toy_slr_m=0.2t+(H-0.2)t²`, where H is 0.45/0.65/1.00 m. Probability is `1/(1+exp((elevation_m-toy_slr_m-0.7)/0.55))`. These are transparent pedagogical choices, not IPCC projection values. Probabilities are rounded to eight decimal places. `dashboard-data.json` contains the same facility and panel records for JavaScript.

## Other bundled tables

- `ipcc_ar5_reference.csv`: six global reference rows; fields `scenario`, `period`, `baseline`, `mean_m`, `likely_low_m`, `likely_high_m`, `source`. Baseline 1986–2005; periods 2046–2065 and 2081–2100. Metres; do not treat as local point projections or exact 2100 values.
- `poster_findings.csv`: the narrative's 108, 2.8× and 3.8× statements, separately from recalculations; fields `metric`, `scenario`, `value`, `unit`, `provenance`.
- `natural-earth-land.geojson`: Natural Earth v5.1.2, 1:110m land geometry, longitude/latitude WGS84. Preserved upstream geometry; only geometry is used by charts. No facility classification uses this basemap.
- `provenance.json`: source URLs, retrieval date, transformation descriptions, rights notes and SHA-256 hashes of bundled data and teaching media.

## Original Power BI field crosswalk (schema documentation only)

| Source field(s) | Observed role | Public teaching equivalent / caution |
|---|---|---|
| uid | Original site identifier | Fictional `facility_id`; never exported |
| Latitude, Longitude | Original facility coordinates | Fictional coordinates; public map uses city anchors |
| CNTRYNAME, CITYNAME, CITYNAME2, CITYNAMESJ | Country/city and join-derived names | `country`, `city`; resolve original join rules before replication |
| ACTUALE → ACTUAL_MHHW_ELEV_M | Model renames source elevation column | `elevation_m` has a different, explicitly fictional datum |
| EFFECTIVEE | Effective elevation input | No equivalence claimed without PAT metadata |
| DEM | Elevation product identifier | Fictional examples do not sample a DEM |
| A20…A90, A00 | RCP 2.6 decade categories | `scenario`, `year` and explicit lab threshold |
| B20…B90, B00 | RCP 4.5 decade categories | Same mapping |
| C20…C90, C00 | RCP 8.5 decade categories | Same mapping |
| RED / ORANGE / YELLOW / NOFILL | Source classification strings | For local public-total reconciliation only, the first three are counted; no invented mapping to exact probabilities |
| R26EAE*, R45EAE*, R85EAE* | Exceedance-related source outputs | Units must be confirmed; observed values exceed 1, so not probability fractions |
| R26ECE*, R45ECE*, R85ECE* | Cumulative exceedance-related outputs | Definition and accumulation window require PAT metadata |
| R26EAE400, R65EAE50, R65ECE50 | Anomalous original names | Flag for review; do not silently rename or infer RCP 6.5 |
| PEPFARSUP | Source 0/1 support flag | Public portfolio totals use 1; fictional flag is independent |
| TXCURR23 | Program-indicator-like field | Not distributed; `service_load` is not a substitute |
| CNT, FLOODA/B/C, FLOODAC, POTA/B/C | Count/flag fields | Do not sum without understanding record grain and time window |
| CLUSTERRANK, FLOODFACS, ALLFACILITIES, LLR, RADIUSKM, OBSVSEXP, PVALUE, RELRISK, GINICLUSTER | SaTScan-related aggregate table | Not reproduced by the fictional scan; source p-values displayed as 0.00 are rounded, not literal zero |

## Aggregation rules

Public cards sum one reporting scope at one scenario/year. Percentages use the ratio of sums, never an unweighted average of group percentages. Fictional cards count distinct facilities once. Service loads are summed only for sites above the chosen probability threshold and represent a hypothetical workload at those sites, not expected lost visits. Listing search does not alter the cohort; the UI says so. Blank/missing source values are not interpreted as zero risk.


## Power BI integration metadata: `powerbi-report.json`

This file stores the original report's page catalog, not facility data. `report_url` is empty until a hosted report is configured; an empty value means **not connected**. `source_file`, `source_member` and `inspected_date` identify the local source of the metadata. Each `pages` entry contains `name` (internal service page identifier), `displayName` (visible report-tab caption), and `ordinal` (zero-based source order). There are 18 pages, including three RCP results pages. Check this catalog against current service metadata if pages are recreated.
