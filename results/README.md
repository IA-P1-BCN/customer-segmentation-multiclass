# Metrics registry convention (US-03)

Every reported metric must come from an executed, recorded run — never
estimated or remembered (AGENTS.md sections 3 and 5). This document defines
the single convention all team members follow when recording metrics
(D-007, item 6: metrics are recorded in `results/` using a common format).

## Location and format

- One CSV file per model in `results/`, named after the model in lowercase
  with underscores (e.g. `results/logistic_regression.csv`).
  One file per model avoids merge conflicts between team members.
- UTF-8, comma-separated, header row required, one row per recorded run.

## Required columns (minimum, per US-03 acceptance criteria)

| Column | Meaning |
|---|---|
| `run_timestamp_utc` | UTC date and time of the run, ISO 8601 (e.g. `2026-11-13T10:30:00Z`) |
| `seed` | Global seed used; always imported from `src.config` (`RANDOM_STATE`), never hardcoded |
| `model` | Model name, matching the file name (e.g. `logistic_regression`) |
| `partition` | Split the row refers to: `train_70`, `val_15`, `test_15` or `cv5fold` |

## Additional columns (justified by D-010)

| Column | Meaning |
|---|---|
| `config` | Short description of the model configuration / hyperparameters |
| `accuracy` | Accuracy of the run (D-010: reported for every model; overfitting check) |
| `macro_f1` | Macro-F1 of the run (D-010: primary metric) |
| `f1_A`, `f1_B`, `f1_C`, `f1_D` | Per-class F1 (D-010: per-class report on validation) |
| `notes` | Free-text observations (e.g. configuration variant, D-009 ceiling) |

## Rules

1. Append rows only; never edit or delete previous rows (append-only log).
2. The `seed` column contains the value imported from `src.config`.
3. The overfitting check (< 5 percentage points between train and validation
   accuracy, D-010) is computed from the `train_70` and `val_15` rows of the
   same run.
4. Cross-validation rows (`cv5fold`) record the mean and standard deviation
   across folds in `notes` when a single row is not enough (D-010, item 6).
5. Files stay in the repository next to the code that produced them, so
   every figure in the report is traceable to a recorded run.

## Example row (illustrative, not a recorded metric)

```csv
run_timestamp_utc,seed,model,config,partition,accuracy,macro_f1,f1_A,f1_B,f1_C,f1_D,notes
2026-11-13T10:30:00Z,42,logistic_regression,baseline,train_70,0.65,0.55,,,,,illustrative example only
```
