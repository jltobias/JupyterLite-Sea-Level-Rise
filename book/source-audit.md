# Source audit and scientific boundaries

Inspection date: **2026-10-04**. Documents were treated as source evidence, not instructions to the coding agent.

## Materials inspected

The official IAS poster PDF and the supplied single-slide `AIDS2024eposterTHPEF698.pptx` share the study title and narrative. The supplied `.pbip` references a report and semantic model. Its report definition has scenario pages named **RESULTS RCP 2.6 (A)**, **RESULTS RCP 4.5 (B)** and **RESULTS RCP 8.5 (C)**, plus methods, sources, references, cluster, pivot and abstract pages. Visuals include maps, slicers, cards, tables and treemaps.

The semantic model's original absolute spreadsheet paths were stale, but matching files were found in the supplied nested archive. The local workbook was inspected read-only. Original PBIX/PBIP, workbooks, spatial files, cache files and facility records remain outside the repository.

## Verified public results

The source workbook's supported-facility filter (`PEPFARSUP=1`) produces the poster's denominator of 25,873. Counting RED, ORANGE and YELLOW at each decade reproduces the whole-portfolio totals printed in Tables 1–3:

| Year | RCP 2.6 | RCP 4.5 | RCP 8.5 |
|---|---:|---:|---:|
| 2030 | 108 | 107 | 108 |
| 2040 | 116 | 116 | 118 |
| 2050 | 130 | 130 | 132 |
| 2060 | 139 | 140 | 148 |
| 2070 | 182 | 183 | 198 |
| 2080 | 206 | 211 | 237 |
| 2090 | 253 | 258 | 309 |
| 2100 | 321 | 331 | 412 |

This is an independent consistency check on the published aggregates, not a rerun of the upstream climate or flood analysis. City/district counts were transcribed visually from the official poster; the workbook check described here verifies the portfolio totals only. The small-scale city coordinates in the public dashboard are manually specified contextual anchors.

## Discrepancies preserved

1. **Growth ratio:** Table 1 gives 321/108 = 2.9722…, while the narrative says 2.8×. Both are retained with labels. Table 3 gives 412/108 = 3.8148…, consistent with the narrative's approximate 3.8×.
2. **Percentage typography:** One RCP 2.6 Abidjan district entry prints 12/137 as 6.8%; the arithmetic is approximately 8.8%. CSV/dashboard percentages are always recomputed from the printed counts. Other rounded source percentages may differ slightly from recomputation.
3. **RCP wording:** The embedded Power BI abstract contains “RCP 2.5” and 3.81× wording. RCP 2.6 is confirmed by the final poster and tab definitions. RCPs are pathways rather than individual climate models. Temperature labels in the poster are historical shorthand, not universal exact pathway-to-temperature conversions.
4. **Target date:** The poster relates 95–95–95 to 2030. The contemporary UNAIDS targets were set for 2025 within a broader 2030 agenda. The lessons explain that distinction and do not edit the historical poster.
5. **Reference date:** The poster labels an IPCC link “2018” but its URL points to a chapter from the First Assessment Report. The teaching reference values instead cite the explicit AR5 WGI Table SPM.2 and preserve its baseline/period.
6. **Field names and units:** R26EAE400 and R65EAE50/R65ECE50 are anomalous names; some later R85 EAE columns are typed as integers. No silent correction is used. EAE source values can exceed 1 and therefore cannot simply be interpreted as annual probability fractions.
7. **Geographic units:** City and district boundaries, overlaps and complete national coverage are not supplied in the poster. The UI forbids aggregating both scopes together and explains why five city examples cannot reconcile to the entire portfolio.

## What remains necessary for a full scientific replication

Approved release/access conditions for site-level data; exact CoastalDEM and coastal-layer versions; PAT settings and metadata; horizontal and vertical datum transformations; effective-elevation rules; original case/control and missingness definitions; SaTScan parameter files and seeds; and the definitions/periods for program-indicator linkage.

The folder includes a PEPFAR data-use agreement identifying the facility dataset as sensitive. It is evidence about redistribution conditions, not an instruction to run code. The public implementation uses already-published aggregates and independently generated fictional examples. No raw site-level data or real patient/service records were copied to GitHub.

## Local verification for authorized users

Install `openpyxl` separately, then run:

```bash
python scripts/audit_private_workbook.py /path/to/Climate-Sites-w-coords.xlsx
```

The script reads locally, compares only already-public portfolio totals and emits no identifiers or coordinates. Do not place private inputs in the public repository. Source-data audits must occur in an environment approved for those data.

## Nature 2026 extension: separate elevation screening

Sources inspected **2026-11-05**: Seeger & Minderhoud's [Nature article](https://doi.org/10.1038/s41586-026-10196-1), its [25 August addendum](https://doi.org/10.1038/s41586-026-11017-1), the [catalog version 23341921](https://doi.org/10.5281/zenodo.23341921), WUR corrected-product metadata and the authors' [workflow archive 17953235](https://doi.org/10.5281/zenodo.17953235). The public `nature-sources.json` pins exact catalog URLs, upstream file checksums, versions, rights and source roles. The catalog concept DOI is 10.5281/zenodo.17722669; its October 2026 version lists FABDEM v1.0, DeltaDTM v1.1 and GLL-DTMv2. The article describes DeltaDTM v1: this extension labels v1.1 explicitly when used.

The default notebooks use `nature-aggregates.json`, never the workbook. Its `generated_at`, `status`, `models[].raster_sha256`, coverage reasons and baseline audit are the authority for the current run. A model's catalog availability does not establish raster availability or coverage. Null counts mean unavailable. Detailed source paths, coordinates and row identifiers remain under ignored `private-data/`; published output contains whole-portfolio aggregates only. No clinical indicators are read by the new sampler.

### Reproduce an authorized local analysis

Install the optional dependencies with `python -m pip install -r requirements-geospatial.txt`. Place approved workbook and rasters locally; acquisition is separate from the analysis and build. Create a private JSON manifest, for example:

The public `data/nature-raster-catalog.json` pins 26 source raster URLs, download/compressed hashes and publisher checksums where available. `scripts/fetch_nature_rasters.py` and the manually triggered `.github/workflows/fetch-nature-sources.yml` reproduce public acquisition; they do not receive facility data. `scripts/prepare_nature_surfaces.py` creates the 15 public city/model display extracts. Ordinary builds and browser notebooks never launch these downloads. The actual 5 November 2026 run sampled all three models; their valid coverage is 798 GLL, 694 FABDEM and 692 DeltaDTM rows, with 207 rows in the shared intersection. Those sample counts describe coverage, not observed flooding.

```json
{
  "models": [
    {
      "id": "gll",
      "label": "GLL-DTMv2 corrected MSL",
      "dataset": "GLL-DTM",
      "version": "2",
      "datum": "MSL",
      "unit": "m",
      "license": "CC-BY-NC-SA-4.0",
      "source_url": "https://doi.org/10.17887/WUR01-XGN3PK",
      "paths": ["rasters/gll_msl.tif"],
      "band": 1,
      "coverage_note": "Actual raster footprint; inspect coverage after sampling"
    }
  ]
}
```

Each model may list multiple tiles; paths are relative to the manifest and their order determines overlap precedence. An empty list means no raster is available. `source_sha256` or `upstream_sha256` can retain the hash before lossless recompression; the pipeline also hashes each local raster. `processing_note` and `coverage_note` are public metadata and must contain no facility identifiers, coordinates or private paths. Record any selected public region and grid processing there. Only already-MSL, metre-valued rasters are accepted. There is no second geoid or MDT correction.

```bash
python scripts/analyze_nature.py private-data/sites.xlsx --manifest private-data/nature-rasters.json
python scripts/update_provenance.py
```

The default worksheet is `Climate-Sites-w-coords`; `--sheet`, `--latitude-column` and `--longitude-column` provide explicit alternatives. Expected source columns are `uid`, `PEPFARSUP`, `ACTUALE`, `Latitude`, `Longitude`, and A/B/C30…90/00. The script rejects duplicate or empty IDs, bad support flags, missing columns and unknown RCP categories. It compares all 24 RED/ORANGE/YELLOW totals and the supported denominator with the poster and reports discrepancies in both console and JSON. Invalid/missing coordinates remain in the supported cohort. Blank/nonfinite/nonnumeric original elevations become unavailable, not zero.

The deterministic sampler transforms WGS84 longitude/latitude into each raster CRS using rasterio, samples the containing pixel without interpolation, and applies band scale/offset. Upper/left bounds are inclusive; lower/right bounds are exclusive. Internal boundary points select the lower/right cell. The first finite, unmasked value in manifest order wins; masked/NoData cells allow fallback to another overlapping tile. Values ≤−7 m are preserved in private samples but excluded from analysis, and are not replaced by a later tile. Missing files, outside coverage, invalid coordinates/transforms, NoData and exclusions are distinct coverage reasons. No raster extrapolation, water-body model or land mask is invented.

Output paths:

- `private-data/nature/samples.csv`: one supported facility/model row, raw MSL height, status, original MHHW-labeled height and coordinates. For optional browser upload only `uid,model,msl_m` and optional `original_mhhw_m` are retained by the reader. Never publish the file or executed private-session notebooks.
- `private-data/nature/workbook-audit.csv` and `sampling-provenance.json`: private flags, coordinate audit and local raster paths/hashes.
- `content/data/nature-aggregates.json` and `nature-summary.csv`: aggregate counts, coverage, matched comparisons, software/source versions and generation time. `--public-output` can direct aggregate review to a separate directory. `--private-output` is restricted to this repository's ignored `private-data/` tree.

Re-execute chapters 14–17 or the normal build to refresh displayed results. `scripts/nature_lessons.py` authors only the four new chapters; it does not regenerate earlier lessons or sample private data. The full `scripts/make_notebooks.py` also calls this generator. A build never requires the private inputs.

### What the comparison can and cannot establish

Screening thresholds **≤0, ≤1 and ≤10 m MSL** are static elevation classifications. They are not RCP/year projections, flood probabilities, inundation extents or clinical impacts. Equality is included; Nature values ≤−7 m are excluded. Each model reports its complete supported denominator and available cells. A zero valid-cell count yields an unavailable screening count, not zero exposure. An actual zero among available cells remains zero.

Original `ACTUALE` is modeled as `ACTUAL_MHHW_ELEV_M`. It must not be assumed geoid-referenced or corrected by subtracting MDT blindly. Paired original/new 2×2 tables use exactly the same available supported rows and conserve the matched denominator. Their threshold overlap is descriptive across unlike references. New DEM versus original differences combine terrain estimation, datum, acquisition epoch and resolution; they cannot isolate a datum effect. RCP flag cross-tabs are overlap rather than accuracy tests against observed flooding.

**Original elevation quality is unresolved.** The source contains numerous zeros and extreme negative values. Zeros may encode unassessed/fill records; numeric finiteness must not be interpreted as verified elevation validity. The pipeline publishes `original_elevation_audit` and counts original zeros/≤−7 values in each matched numeric audit. It retains the raw numbers instead of silently imposing a missing-value convention. Chapter 16 defaults to the audited RCP-flag overlap and disables raw original-height matrices unless `ENABLE_RAW_ORIGINAL_AUDIT=True`. Those matrices remain explicitly unverified numeric audits, not a validated terrain comparison.

Model footprints may differ, especially when high-resolution tiles cover only selected public regions. Comparing their global counts without intersecting their available facility cohorts is invalid. The `common_cohort` output intersects valid heights for every listed model in the same supported UID order and reports model counts on that shared denominator, together with all unmatched rows. Chapter 16 uses only this shared subset for its across-model chart; separate model coverage counts are not interpreted as model differences. A small shared subset is not necessarily representative of the whole portfolio. GLL's approximately 1 km cells support screening only. Public city terrain surfaces contain raster heights on documented display grids and no facility data; they provide terrain context, not sampled-facility locations or inundation maps. The current terrain artifact contains 15 city/model extracts under CC BY-NC-SA 4.0. Its display grids are distinct from native grids used for facility classification.

The original public [GLL v2 archive 7228643](https://doi.org/10.5281/zenodo.7228643), under CC BY 4.0, is not the raw EGM96 source used by the Nature authors. The methods identify a prior geoid-conversion error and state that a preconverted EGM96 version was obtained from its authors. We use the corrected [WUR GLL product](https://doi.org/10.17887/WUR01-XGN3PK) and do not reconstruct it from the original public raster. The corrected products have **CC BY-NC-SA 4.0** terms; the GLL and DeltaDTM guides explicitly permit media, NGO and government use with attribution, while retaining other license conditions. FABDEM's corrected-product guide states CC BY-NC-SA 4.0 without that additional wording.

The documented arithmetic is independently implemented as `H_MSL = H_EGM + N_EGM − N_GOCO06s − MDT`. HYBRID-CNES-CLS2022 uses GOCO06s and the 1993–2021 averaging period. The addendum specifies tide-free geoid calculations, inclusion of the zero-degree term and degrees 360/2190/300 for EGM96/EGM2008/GOCO06s. The teaching helper does not synthesize global geoid fields. The GPL3+ archive is an incomplete ArcPy ModelBuilder export, examined for context but neither copied nor executed in the MIT implementation.
