# SARS-CoV-2 Antibody Escape Prediction

Flask web application for SARS-CoV-2 variant identification, spike mutation detection, and Casirivimab/Imdevimab cocktail neutralization (IC50) prediction.

Documentation pack: `D:\covid_website_summary`

---

## Quick Start

```powershell
cd D:\covid_website_project
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 — upload a `.fasta` file and click **Predict Antibody Escape**.

Restart Flask after code or model changes.

---

## Project Structure

```
covid_website_project/
├── app.py                          # Flask entry point
├── requirements.txt
├── README.md                       # This file
├── templates/index.html            # Web UI
├── utils/
│   ├── paths.py                    # Central data path constants
│   ├── sequence_comparator.py      # Variant identification (14 NCBI refs)
│   ├── sequence_analyzer.py        # Spike extraction + mutation calling
│   └── neutralization_predictor.py # Ridge IC50 models
├── data/
│   ├── README.md                   # Train / prediction / evaluation guide
│   ├── training/                   # ML training data + models
│   ├── prediction/                 # Reference genomes for web runtime
│   └── evaluation/                 # Held-out test config & results
├── scripts/
│   ├── run_evaluation.py           # One-click test reproduction
│   ├── split_ml_dataset.py
│   ├── train_neutralization_model.py
│   ├── evaluate_ml_test_set.py
│   ├── evaluate_pipeline_test_set.py
│   ├── batch_test_variants.py      # Internal regression only
│   ├── download_variants.py
│   ├── build_ml_features.py        # Rebuild feature matrix (optional)
│   └── sync_submission_pack.py     # Sync summary folder for hand-in
└── overleaf/                       # Final report LaTeX source
```

See **`data/README.md`** for the train vs prediction vs evaluation split.

---

## Reproduce Report Metrics (Held-Out Test)

Do **not** use the 14-strain batch run as the primary ML accuracy metric — BA.1, BQ.1.1, and Beta overlap with training data.

```powershell
.\.venv\Scripts\python.exe scripts\run_evaluation.py
```

| Test set | Samples | Metric | Result |
|----------|---------|--------|--------|
| Pipeline test | 6 NCBI strains | Variant ID + mutation recall | 6/6, 100% |
| ML test | 18 CoV-UniBind rows | log10(fold) MAE / r | MAE 0.349, r 0.934 |

Outputs: `data/evaluation/ml_test_results.json`, `pipeline_test_results.json`

---

## Recommended Test Files

| Variant | Path |
|---------|------|
| Wild Type | `data/prediction/wuhan_hu1_complete.fasta` |
| Gamma (P.1) | `data/prediction/gamma_complete.fasta` |
| Delta | `data/prediction/delta_complete.fasta` |
| JN.1 | `data/prediction/jn1_complete.fasta` |

Do **not** use course `gamma_data.txt` (MZ477859.1) — it is near wild-type, not true P.1.

---

## API

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main page |
| `/upload` | POST | Upload FASTA, returns JSON analysis |
| `/health` | GET | Service status + model readiness |

---

## Dependencies

Python 3.10+, see `requirements.txt`: Flask, Biopython, pandas, scikit-learn, joblib, numpy.

---

## Sync Submission Pack

```powershell
.\.venv\Scripts\python.exe scripts\sync_submission_pack.py
```

Updates `D:\covid_website_summary` with latest evaluation results, docs, and Overleaf ZIP.
