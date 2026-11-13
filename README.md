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
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Reference environment: Python 3.12.3 (see A-009 / A-012).

## Reproducibility
- Global seed: `RANDOM_STATE = 42` in `src/config.py`. Always import it; never hardcode.
- Split: `python src/split_data.py` generates `data/train_70.csv`, `data/val_15.csv` and `data/test_15.csv`.
- Primary metric: macro-F1 on validation; accuracy is also reported. Overfitting: absolute accuracy difference < 5 points between train and validation (D-010).

## Repository structure
```
data/            # Train.csv + splits (train_70, val_15, test_15)
src/             # split_data.py, config.py, data_quality.py, (Pipeline US-05)
results/         # per-model metrics (convention in results/README.md)
reports/         # EDA figures and tables (nulls, etc.)
docs/ai-usage/   # DECISION_LOG.md, AI_ACTIVITY_LOG.md
01_eda_inicial.ipynb
requirements.txt
AGENTS.md
```

## How to run
- **EDA:** open `01_eda_inicial.ipynb` (Jupyter/VS Code) and run "Restart & Run All".
- **Models:** notebooks/scripts under `feature/model-*` (logistic regression, random forest, boosting, SVM) importing the shared Pipeline from `src/`.
- **App:** *(pending — US-15)* `streamlit run app.py`
- **Technical report:** *(pending — US-16)* see `reports/` and the report.

## Main results
- Baseline (majority class, D): accuracy ≈ 28.1 %, macro-F1 ≈ 0.11 (D-010).
- *(Pending — US-11)* Frozen best model, test metrics and feature importance.

## Board
- GitHub Project #58: https://github.com/orgs/IA-P1-BCN/projects/58

## Decisions and traceability
- [Decision Log](docs/ai-usage/DECISION_LOG.md) — D-001 to D-013.
- [AI Activity Log](docs/ai-usage/AI_ACTIVITY_LOG.md) — A-001 to A-012.
- Git workflow: `feature/* → develop → main`, with Squash Merge into `develop`.

## License
Dataset under CC0. Project code: to be defined by the team.
