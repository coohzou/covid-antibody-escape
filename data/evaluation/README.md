# Evaluation Data

## Train / test splits

- **ML test** (`data/training/ml_test.csv`): 18 rows, 4 held-out isoforms from CoV-UniBind; excluded from training.
- **Pipeline test** (6 variants in `split_config.json`): Alpha, Gamma, Delta, Omicron, BA.4, JN.1.

See `split_config.json` for rules.

## Output files

```
data/evaluation/split_config.json
data/evaluation/split_summary.json
data/evaluation/ml_test_results.json
data/evaluation/pipeline_test_results.json
data/evaluation/pipeline_test_summary.csv
data/evaluation/internal/batch_test_*
```

## Run

```powershell
python scripts/run_evaluation.py
```

See `data/README.md` for the full data layout.
