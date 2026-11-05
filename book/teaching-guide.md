# Teaching guide

## Workshop structure

| Session | Activities | Evidence of learning |
|---|---|---|
| 1. Read the study (75 min) | 00–01; public dashboard; identify numerator/denominator | One result sentence and the 2.8×/2.97× discrepancy |
| 2. Explain the scenarios (75 min) | 02–03; baseline/interval reading; probability experiment | Correct annual-vs-cumulative calculation |
| 3. Build the views (120 min) | 04–08; joins, slicers, animation, terrain and cube | Reconciled dashboard and appropriate visual encoding |
| 4. Test and plan (120 min) | 09–10; scan experiment and capacity network | Transparent methods and continuity memo |
| 5. Capstone (60–90 min) | 11–12; peer review, sources and reproducibility | Downloaded notebook, CSV, plots and evidence manifest |

These are suggested group timings; individual chapter estimates include reading and optional practice. Exercises use published and fictional data only. No learner needs credentials to the original PEPFAR or Climate Central datasets.

## Before class

Open the live site in the actual teaching environment and run notebook 00. Allow the first Pyodide/package download to finish. Test WebGL; if disabled, use the 2D map, heatmaps and tables. The dashboard needs no Python kernel. A static reading path is available if a school network blocks Python runtime downloads.

## Facilitation prompts

- Which quantity is observed, reported, projected or invented?
- What is the unit of a row, and what is the denominator of this card?
- Could the same facility appear in more than one reporting group?
- Does a flooded road change your recommendation even if the clinic stays dry?
- Whose priorities determine the threshold or decision weights?
- What evidence would make you revise this conclusion?

## Accessibility and media

All controls have labels and visible focus states. Tables accompany graphical views. Use the fixed-scale heatmap when rotation or animation is inaccessible. Animations require an explicit play action and can be paused. The generated video has captions and a transcript and contains no audio. The conceptual comic includes alt text and is labeled as AI-generated.

## Assessment

Use the capstone's 20-point rubric. A visually impressive figure with an incorrect denominator should not pass the reproducibility criterion. Reward clear uncertainty statements and a defensible source trail. For advanced learners, extend the data contracts and compare alternative dependence assumptions; do not present the fictional scan as validated SaTScan replication.

## Troubleshooting

If a notebook cannot import its helper, open it from the bundled `notebooks/` folder and run the setup cell. If Python cannot fetch packages, check network policies and use the standalone dashboard while resolving access. If a notebook's old browser copy masks a newer server version, download your edits first, then remove/rename the old browser copy or open a clean browser profile. Do not clear browser storage before exporting work.

## Nature 2026 workshop: chapters 14–17

Allow 2–3 hours: chapter 14 for reference surfaces and sign checks; chapter 15 for exact source versions and coverage; chapter 16 for the AIDS 2024 baseline and matched overlap; chapter 17 for fictional 3D surfaces and interactive sensitivity. The default route uses public aggregates and invented examples, with no private upload or GIS installation.

Assess four distinctions: MHHW versus MSL; unavailable versus zero; matched overlap versus accuracy; and static elevation screening versus probabilistic flooding. Ask learners to show that their matrix conserves the matched cohort. A stronger answer names terrain source, epoch and resolution as additional explanations for original/new differences.

The threshold dropdown in chapter 16 reads the published aggregates; a missing model remains unavailable. Chapter 17's two sliders change an explicitly fictional fixture reproducibly. Its optional private CSV upload is for authorized individual sessions only; do not use real records in classroom screen sharing, shared notebooks or published outputs. Tables accompany plots, including the 3D surface example. A disabled WebGL environment can use the tables and 2D views.

Optional advanced work uses the local rasterio workflow documented in the source audit. Keep the detail files under `private-data/`, review the aggregate coverage and source hashes, and then rebuild. High-resolution regional coverage cannot be compared directly with GLL's broader cohort; chapter 16's across-model chart first intersects valid supported rows in all models and reports that smaller shared denominator. Discuss whether this subset is representative. Missing rasters are an opportunity to write a coverage-aware interpretation, not a reason to substitute fictional counts for results.
