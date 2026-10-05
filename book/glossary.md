# Glossary

| Term | Meaning in this book |
|---|---|
| Adaptation | Adjusting systems and decisions to reduce harm under climate conditions. |
| Annual exceedance probability (AEP) | Probability a specified water level or event threshold is exceeded at least once in one year; a fraction from 0 to 1. |
| Annual event rate | Expected number of events per year; may exceed 1. It is not the same quantity as AEP. |
| ART | Antiretroviral therapy. Service exposure does not determine an individual's clinical outcome. |
| Baseline | Reference period or level against which change is measured. |
| Bernoulli scan | Spatial comparison of binary case/control status inside and outside candidate windows. |
| Card | A dashboard display of an aggregate metric under the active filters. |
| Climate model | A representation of the climate system's physical behavior. A scenario is an input condition, not the model itself. |
| CoastalDEM | Climate Central's coastal elevation product; versions, licenses and errors must be specified. |
| Cohort | The set of facilities/reporting groups selected before calculating metrics. |
| Continuity of care | Maintaining access to essential services over time and through disruption. |
| CRS | Coordinate reference system defining how coordinates relate to the Earth. |
| Cumulative probability | Probability of at least one event across a stated period, under explicit temporal dependence assumptions. |
| DATIM | Data for Accountability, Transparency and Impact Monitoring; the source UID supports authorized linkage. |
| DEM | Digital elevation model; a gridded representation of heights relative to a specified datum. |
| Denominator | The reference population or count used to calculate a fraction; 25,873 for the published 2023 supported portfolio. |
| Effective elevation | A source-specific metric that may differ from ground elevation; its exact PAT definition must come from metadata. |
| EPSG:4326 | A WGS84 geographic coordinate system, conventionally longitude/latitude in this repository's files. |
| Equity | Considering unfair differences in exposure, resources, access and decision-making power. |
| Exposure | Presence of people, infrastructure or services where a hazard may occur. |
| Gini cluster selection | A SaTScan cluster-reporting approach; not implemented by the teaching scan experiment. |
| Hazard | A potentially damaging physical event or condition, such as coastal flooding. |
| Hotspot | A concentration defined using a stated spatial/statistical rule; not simply a large marker. |
| Inundation | Water covering land; a low-elevation mask alone does not establish actual inundation. |
| Likely range | A calibrated uncertainty interval whose meaning must be taken from the assessment that reports it. |
| LLR | Log-likelihood ratio comparing fitted alternative and null hypotheses. |
| MHHW | Mean higher high water, a tidal datum based on the higher daily high-water level over a defined period. |
| Mitigation (climate) | Reducing greenhouse gas emissions or enhancing removals. Distinguish from reducing local disaster consequences. |
| Monte Carlo test | A test using repeated simulated or permuted data to approximate a null distribution. |
| PAT | Climate Central Portfolio Analysis Tool, used in the poster; not rerun by this public teaching repository. |
| PEPFAR | U.S. President's Emergency Plan for AIDS Relief. Historical study context, not an assertion of current program scope. |
| Projection | A conditional future outcome under specified assumptions. |
| Radiative forcing | A change in Earth's energy balance, typically expressed in W/m². |
| RCP | Representative Concentration Pathway. The poster compares RCP 2.6, 4.5 and 8.5. |
| Relative sea level | Sea-surface height relative to local land, incorporating both ocean change and land motion. |
| Resilience | Capacity to prepare for, absorb, adapt to and recover from disruption. |
| Return period | Inverse of annual exceedance probability under stationary assumptions; not a scheduled interval. |
| Risk | Potential adverse consequences of hazards interacting with exposure and vulnerability. |
| SaTScan | Software for spatial, temporal and space–time scan statistics. |
| Slicer | A control selecting the cohort or dimension values used by dashboard results. |
| Space–time cube | A display with two spatial axes and a time axis; height is time, not terrain. |
| SSP | Shared Socioeconomic Pathway; newer scenario frameworks should not be silently substituted for RCPs. |
| Storm surge | Sea-level change caused by storm-driven winds and atmospheric pressure; distinct from astronomical tides. |
| Synthetic / fictional data | Data generated independently for demonstration; not anonymized or perturbed real facilities here. |
| TX_CURR | A treatment-current program indicator; use the applicable official definition and reporting period before analysis. |
| UID | Unique identifier; pseudonymous identifiers do not eliminate disclosure risk. |
| Vertical datum | Reference surface used for heights; must be consistent between elevation and water-level inputs. |
| Vulnerability | Conditions that make exposed people or systems more susceptible to harm. |
| 95–95–95 | Conditional testing, treatment and viral-suppression cascade targets, set for 2025 in the historical UNAIDS framework. The wider ending-AIDS agenda targets 2030. |

Definitions are teaching summaries; source-specific metadata takes precedence when interpreting a dataset. See the [references](references.md) for IPCC, UNAIDS, Climate Central and SaTScan documentation.


## Power BI integration terms

- **PBIX:** Power BI Desktop report/model file; not executable browser code.
- **Power BI Service:** Microsoft's hosted report and semantic-model platform.
- **Secure embed:** An authenticated report viewer placed in another page; existing access rules still apply.
- **Report page name:** Internal page identifier used in API calls and `pageName` links; distinct from a visible tab caption.
- **python-power-bi:** Unofficial Python REST API wrapper used for metadata in chapter 13; not a report rendering engine.
- **powerbiclient:** Microsoft's notebook widget package for embedding hosted Power BI reports; not a local PBIX renderer.
