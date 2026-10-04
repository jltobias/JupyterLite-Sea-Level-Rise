# Coastal Futures

## Sea-level rise, health facilities and continuity of care

An executable learning book based on **Tobias et al., “PEPFAR Adapts to Sea Level Rise and Storm-Surge: Potential Impacts to Coastal Cities and Facilities (2030)”**, presented at AIDS 2024, poster THPEF698.

<a href="https://plus.iasociety.org/sites/default/files/2024-09/e-poster_755.pdf">Read the official AIDS 2024 poster</a> · <a href="../lite/lab/index.html?path=notebooks/00_start_here.ipynb">Open JupyterLite</a> · <a href="../dashboard/index.html">Explore the dashboard</a>

![AIDS 2024 poster, including methods, three RCP scenario maps, published tables, results and references.](assets/aids-2024-poster.png)

*Poster preview rendered from the official IAS-hosted PDF. Original authors, organizations and third-party figure owners retain their rights. Click the official link for the full-resolution source.*

## Begin with a question

What could rising coastal water levels mean for continuity of HIV services? Work from the published evidence to progressively more demanding maps, interactive dashboards and modeling experiments. Every chapter has learning objectives, executable examples, a lab and a worked interpretation.

The book includes **13 notebooks**, **264 public poster aggregate rows**, and a separate reproducible dataset of **192 fictional facilities × 3 scenarios × 9 decades**. The original sensitive site records and proprietary elevation/flood layers are not distributed.

## Choose your route

- **First encounter, 60–90 minutes:** chapters 00, 01 and 05. Explore the public results and learn to reconcile filters and counts.
- **Visualization studio, half day:** chapters 02–08. Learn probabilities, tidy data, animated maps, 3D scenes and space–time cubes.
- **Methods and planning workshop:** chapters 09–12. Test a fictional scan statistic, examine service continuity, complete a capstone and write a reproducibility plan.

## Reading and running

This Jupyter Book provides saved outputs and interactive browser dashboards. Each notebook also has a **Run in JupyterLite** link. In JupyterLite choose **Run → Run All Cells**. Python runs in your browser through Pyodide; the first launch downloads the runtime and packages. Modern Chrome, Edge or Firefox is recommended. The 3D views need WebGL; the tables and 2D charts provide alternatives.

Edits live in browser storage. Download notebooks and CSVs to preserve work; clearing browser storage can erase edits. The read-only dashboard bundles its chart library and basemap locally. JupyterLite's initial runtime/package downloads require network access; this is not a fully offline kernel distribution.

## Read the evidence labels

**Published** means transcribed from Tables 1–3 of the official poster. **Reference** means a separately cited historical assessment. **Fictional** means invented examples for learning, not PEPFAR or Climate Central results. Public city pins are approximate city anchors; they never identify facilities.

The source has important limitations and internal inconsistencies. In particular, 321/108 from Table 1 is about 2.97× while the narrative reports 2.8×. The book preserves the narrative and table values separately, recomputes percentages from counts, and documents the distinction in the [source audit](source-audit.md).
