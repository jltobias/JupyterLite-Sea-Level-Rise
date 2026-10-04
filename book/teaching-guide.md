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
