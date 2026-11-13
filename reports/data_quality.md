# Data quality report (US-04)

Generated on 2026-11-12 20:08 UTC by `src/data_quality.py`.

## How to reproduce

```
python src/data_quality.py
```

| Item | Value |
|---|---|
| Interpreter | `F:\venvs\ia-workshop\Scripts\python.exe` |
| Python | 3.12.3 |
| pandas | 3.1.1 |
| Platform | Windows-10-10.0.19045-SP0 |
| Train split | `data/train_70.csv` (5,647 rows) |
| ID source | `data/Train.csv` (8,068 rows) |

## 1. Missing values per variable (train split)

Computed on `train_70.csv` only (5,647 rows, 11 columns). The validation and test splits are not used.

| Variable | Type | Missing | Missing % | Unique (non-null) |
|---|---|---:|---:|---:|
| `Work_Experience` | float64 | 563 | 9.97 % | 15 |
| `Family_Size` | float64 | 244 | 4.32 % | 9 |
| `Ever_Married` | str | 99 | 1.75 % | 2 |
| `Profession` | str | 89 | 1.58 % | 9 |
| `Graduated` | str | 53 | 0.94 % | 2 |
| `Var_1` | str | 50 | 0.89 % | 7 |

Variables without missing values: `ID`, `Gender`, `Age`, `Spending_Score`, `Segmentation`.

## 2. Full table

| # | Variable | Type | Missing | Missing % |
|---:|---|---|---:|---:|
| 1 | `ID` | int64 | 0 | 0.00 % |
| 2 | `Gender` | str | 0 | 0.00 % |
| 3 | `Ever_Married` | str | 99 | 1.75 % |
| 4 | `Age` | int64 | 0 | 0.00 % |
| 5 | `Graduated` | str | 53 | 0.94 % |
| 6 | `Profession` | str | 89 | 1.58 % |
| 7 | `Work_Experience` | float64 | 563 | 9.97 % |
| 8 | `Spending_Score` | str | 0 | 0.00 % |
| 9 | `Family_Size` | float64 | 244 | 4.32 % |
| 10 | `Var_1` | str | 50 | 0.89 % |
| 11 | `Segmentation` | str | 0 | 0.00 % |

Machine-readable version: `reports/nulls_train_70.csv`.

## 3. Duplicated IDs in `Train.csv`

- Rows: 8,068
- Unique `ID` values: 8,068
- Duplicated `ID` values (rows after the first): 0

**Result:** no duplicated IDs. The source file can be split and joined by `ID` safely.

## 4. Proposed imputation strategy (D-011, pending approval)

All values (median, mode and the `Unknown` level) must be computed with `train_70` only and applied inside the Pipeline (`SimpleImputer` fitted on the training fold), never on the full dataset.

| Variable | Missing % | Strategy | Evidence in train |
|---|---:|---|---|
| `Ever_Married` | 1.75 % | mode | mode = Yes (3,264 rows, 58.8 % of non-null) |
| `Graduated` | 0.94 % | mode | mode = Yes (3,490 rows, 62.4 % of non-null) |
| `Profession` | 1.58 % | constant:Unknown | mode = Artist (1,746 rows, 31.4 % of non-null) |
| `Work_Experience` | 9.97 % | median + missing indicator | median = 1 (min 0, max 14) |
| `Family_Size` | 4.32 % | median + missing indicator | median = 3 (min 1, max 9) |
| `Var_1` | 0.89 % | mode | mode = Cat_6 (3,693 rows, 66.0 % of non-null) |

Notes:

- Missing indicators are binary columns added per variable (`<variable>_was_missing`); they keep the information contained in the fact that the value was absent.
- Variables with 0 % missing get no imputation step, which keeps the Pipeline simple and avoids unnecessary transformed columns.
- `ID` and `Segmentation` are never imputed: the first is an identifier and the second is the target.

