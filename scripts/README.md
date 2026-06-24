# Scripts

| Script | Purpose |
|--------|---------|
| `run_evaluation.py` | **One-click**: split → train → ML test → pipeline test |
| `sync_submission_pack.py` | Sync results/docs to `D:\covid_website_summary` |
| `split_ml_dataset.py` | Split `processed_ml_features.csv` into train/test |
| `train_neutralization_model.py` | Train Ridge models on `ml_train.csv` only |
| `evaluate_ml_test_set.py` | IC50 metrics on held-out `ml_test.csv` |
| `evaluate_pipeline_test_set.py` | Variant ID + mutation recall on 6 NCBI strains |
| `batch_test_variants.py` | 14-strain internal regression → `data/evaluation/internal/` |
| `download_variants.py` | Re-download reference FASTA from NCBI |
| `build_ml_features.py` | Rebuild `processed_ml_features.csv` (optional) |
| `export_batch_summary.py` | Export internal batch results to CSV |
| `find_accessions.py` | Utility: look up NCBI accessions |

## Typical workflows

```powershell
# Reproduce report metrics
.\.venv\Scripts\python.exe scripts\run_evaluation.py

# Refresh submission pack
.\.venv\Scripts\python.exe scripts\sync_submission_pack.py

# Start web app
.\.venv\Scripts\python.exe app.py
```
