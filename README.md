# Customer Segmentation — Multiclass Minds

Multiclass classification of customers into segments A, B, C and D from demographic and behavioral data. M2 project (Data Analytics & Machine Learning), Essential level, delivery 18/11/2026.

## Team
Rita, Isbel, Pedro and Brian.

## Dataset
- **Source:** [Kaggle – Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)
- **Complementary reference:** [Analytics Vidhya – JanataHack: Customer Segmentation](https://datahack.analyticsvidhya.com/contest/janatahack-customer-segmentation/)
- **License:** CC0 (confirmed on Kaggle), which allows redistribution of the dataset in this repository.
- `Train.csv` is the only data source. It is split once into `train_70.csv`, `val_15.csv` and `test_15.csv` (70/15/15, stratified by `Segmentation`, `random_state=42`).
- The original Kaggle `Test.csv` **is not part of the project dataset/repository** (D-012). The project's test set is `test_15.csv`.
- Target variable: `Segmentation` (multiclass; classes A, B, C, D).

## Installation
```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\activate             # Windows (cmd)
.venv\Scripts\Activate.ps1         # Windows (PowerShell)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Reference environment: Python >= 3.12 with the versions pinned in `requirements.txt`
(the freeze and the final evaluation were run on Python 3.12.15, scikit-learn 1.9.1,
xgboost 3.4.1 and joblib 1.6.0).

If the environment is managed with `uv`, the equivalent is:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

**macOS:** XGBoost (US-09) needs OpenMP. If `import xgboost` fails or the model
test in `tests/test_train_boosting.py` crashes with a `libomp` error, install it
once with Homebrew:

```bash
brew install libomp
```

## Reproducibility
- Global seed: `RANDOM_STATE = 42` in `src/config.py`. Always import it; never hardcode.
- Split: `python src/split_data.py` generates `data/train_70.csv`, `data/val_15.csv` and `data/test_15.csv`.
- Primary metric: macro-F1 on validation; accuracy is also reported. Overfitting: absolute accuracy difference < 5 points between train and validation (D-010).
- Configuration selection follows D-015: 5-fold cross-validation on `train_70`, and `val_15` only as the official check.
- The frozen model is fitted on `train_70` only (D-017) and serialised with joblib; `test_15` is evaluated once, at the end (D-012).

## Repository structure
```
data/                  # Train.csv (source) + train_70 / val_15 / test_15
src/                   # config.py, split_data.py, data_quality.py, preprocessing.py (shared Pipeline, US-05)
                       # train_svm.py, train_random_forest.py, train_boosting.py, model_logreg.py (US-07..US-10)
                       # select_config.py, compare_models.py, frozen.py (US-11)
                       # evaluate_final.py (US-12), segment_profile.py (US-13)
results/               # one CSV per model + model_comparison.csv (convention in results/README.md)
reports/               # data quality, EDA synthesis, segment profiles, final metrics, confusion matrices, importance
notebooks/03_modeling/ # logistic regression notebook (US-07)
docs/ai-usage/         # DECISION_LOG.md, AI_ACTIVITY_LOG.md
models/                # generated locally by `compare_models --stage freeze` (git-ignored)
01_eda_inicial.ipynb   # initial EDA on Train.csv
02_eda_train70_*.ipynb # EDA sections on train_70
03_model_random_forest.ipynb
requirements.txt
AGENTS.md
```

## How to run

- **EDA:** open `01_eda_inicial.ipynb` (Jupyter/VS Code) and run "Restart & Run All". The per-section notebooks are `02_eda_train70_gasto_estado_civil.ipynb`, `03_eda_train70_brian_outliers_fuga.ipynb`, `04_eda_train70_duplicados.ipynb` and `notebooks/03_modeling/01_logistic_regression.ipynb`.
- **Models (US-07 to US-10):**

    ```bash
    python -m src.train_svm --stage baseline && python -m src.train_svm --stage tune
    python -m src.train_random_forest --stage baseline && python -m src.train_random_forest --stage tune
    python src/train_boosting.py --baseline --grid --refine
    python src/train_boosting.py --select      # D-015 choice, marked SELECTED in results/boosting.csv
    ```

  The logistic regression is the notebook `notebooks/03_modeling/01_logistic_regression.ipynb`.
- **Selection, comparison and freeze (US-11):**

    ```bash
    python -m src.select_config results/boosting.csv               # re-derive one model's D-015 choice
    python -m src.compare_models --stage table --write             # results/model_comparison.csv
    python -m src.compare_models --stage freeze --model boosting   # models/final_model.joblib (git-ignored)
    ```

- **Final evaluation (US-12):**

    ```bash
    python -m src.evaluate_final --model models/final_model.joblib --partition val_15
    python -m src.evaluate_final --model models/final_model.joblib --partition test_15 --allow-test
    ```

  `test_15` is evaluated **once**; the script refuses a second run without `--allow-test-rerun` (D-012).

- **App (US-15):**

    ```bash
    python -m streamlit run app/app.py
    ```

  Loads the frozen XGBoost model from `models/final_model.joblib` (the file must exist locally).
  On macOS, install OpenMP with `brew install libomp` (see Installation).

- **Technical report:** *(pending — US-16)* see `reports/` and the report.
- **Tests:** `python -m pytest`

## Main results

| Model | accuracy (`val_15`) | macro-F1 (`val_15`) | train − val |
|---|---:|---:|---:|
| **XGBoost (selected)** | 0.5430 | **0.5227** | 3.33 pp |
| Random Forest | 0.5248 | 0.5080 | 1.90 pp |
| SVM | 0.5025 | 0.4853 | 3.89 pp |
| Logistic regression | 0.4959 | 0.4786 | 1.64 pp |
| Dummy (majority class) | 0.2810 | 0.1097 | — |

The frozen XGBoost Pipeline (configuration chosen with D-015, trained on `train_70` only, D-017) scores **0.5421 accuracy / 0.5222 macro-F1 on `val_15`** and **0.5599 / 0.5456 on `test_15`**, evaluated once at the end (D-012). Test − validation: +1.77 pp accuracy and +2.34 pp macro-F1. Its train − validation gap is **3.44 pp**, inside the D-010 limit.

The majority-class baseline (D-010) scores 0.2810 accuracy / 0.1097 macro-F1 on `val_15` and **0.2816 / 0.1099 on `test_15`**.

Most important variables (permutation, macro-F1 drop on `val_15`): Age 0.080, Profession 0.077, Spending_Score 0.054, Family_Size 0.029, Graduated 0.017, Gender 0.015, Work_Experience 0.013, Var_1 0.007, Ever_Married 0.006.

Recorded evidence: `results/model_comparison.csv`, `reports/final_metrics_val_15.csv`, `reports/final_metrics_test_15_<timestamp>.csv`, `reports/confusion_*`, `reports/feature_importance_val_15.csv`.

## Board
- GitHub Project #58: https://github.com/orgs/IA-P1-BCN/projects/58

## Decisions and traceability
- [Decision Log](docs/ai-usage/DECISION_LOG.md) — full decision history.
- [AI Activity Log](docs/ai-usage/AI_ACTIVITY_LOG.md) — full activity history.
- Git workflow: `feature/* → develop → main`, with Squash Merge into `develop`.

## License
Dataset under CC0. Project code: to be defined by the team.
