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
