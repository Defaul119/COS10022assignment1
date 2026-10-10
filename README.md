# COS10022 Assignment 1 — Predictive Model Creation and Evaluation

KNIME Analytics Platform 5.12 workflow predicting road-accident survival, plus the report.

| Path | Contents |
|---|---|
| `Assignment_01_2026_v01.pdf` | assignment brief |
| `src/` | input data (unchanged) |
| `final/COS10022_A1_Workflow/` | the KNIME workflow (executed); inputs in `data/src`, outputs in `data/output` |
| `final/verify_outputs.py` | checks the workflow's output files (row counts, class balance, metrics) |
| `final/package_submission.py` | builds the submission zip (workflow `.knwf`, `src/`, `output/`, video) |
| `report/report.tex` / `report.pdf` | the report (screenshots go in `report/figures/`) |
| `report/report_guide.pdf`, `report/workflow_explained.pdf` | study notes |

Run: open `final/COS10022_A1_Workflow` in KNIME (or import the `.knwf` from the submission zip) and click
*Execute all*. All paths are relative to the workflow; all random nodes use seed 2026.

Generative AI (Claude) assisted with this project; see the declaration in the report appendix.
