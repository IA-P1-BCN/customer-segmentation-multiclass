# Technical report: customer segmentation with multiclass classification (US-16)

**Status: draft (2026-11-18).** Rita Pereira integrates the document; each section names who writes or checks it (issue #36). Pedro reviews the whole report before delivery.

| Section | Owner | Status |
|---|---|---|
| 1. Summary | Rita | Draft with the test results (PR #78) |
| 2. Data | Isbel | Draft from approved decisions |
| 3. Methodology and Pipeline | Isbel | Draft from approved decisions |
| 4. Exploratory analysis | Pedro | Draft from the merged US-06 synthesis |
| 5. Models and validation results | Brian | Draft from the recorded results of the four model PRs |
| 6. Final model and test evaluation | Brian | Filled from PR #78 and PR #79 |
| 7. Error analysis | Pedro | 7.1–7.3 filled from the US-12 run; **7.4–7.7 pending US-14** |
| 8. Segments and business reading | Rita | Draft from US-13 part 1 |
| 9. Limitations | Rita | Draft |
| 10. Reproducibility and sources | Rita | Draft |

**How to read the figures.** Every number comes from an executed run recorded in the repository (US-03, AGENTS.md section 5); section 10 lists the source of each one. The model results (sections 3 and 5) were checked against `develop` on 2026-11-17, after the four model PRs were merged. The segment figures (section 8) were checked against `develop` on 2026-11-17, after PR #69 was merged. The final model and test figures (sections 6 and 7) are copied from the files written by the single US-12 run (PR #78, 2026-11-18).

---

## 1. Summary

The project predicts the segment (A, B, C or D) of a customer from nine demographic and behavioural variables, using `Train.csv` from the Kaggle Customer Segmentation dataset. Four models were trained on the same shared partition and preprocessing: multinomial logistic regression, SVM, random forest and XGBoost. Each chose its configuration with the same rule (D-015).

On the validation split (`val_15`), the four selected configurations meet the overfitting limit (train − validation accuracy below 5 points) and clearly beat the majority-class baseline: macro-F1 between 0.4786 and 0.5227, against 0.1097 for the baseline. **XGBoost has the highest validation macro-F1 (0.5227, accuracy 0.5430).** The `val_15` figures of the four models are final.

> **Fixed by D-017 (Approved by Brian, 2026-11-17):** the frozen model is fitted on `train_70` only.
>
> **Final model (US-11, PR #78; D-018 Approved by Pedro, 2026-11-18):** XGBoost, fitted on `train_70`. On `test_15`, opened once, it reaches **accuracy 0.5599 and macro-F1 0.5456**, close to its validation figures (0.5421 and 0.5222) and far above the majority-class baseline on test (0.2816 and 0.1099); its train − validation gap is 3.44 points (section 6). `Age`, `Profession` and `Spending_Score` are the variables the model relies on most (section 6.5).

All models find segment D easiest (F1 about 0.69–0.71 on validation) and segment B hardest (F1 about 0.30–0.37). On test, B has the lowest recall (0.385) and 31 % of the B customers are predicted as C, the pair that the data themselves mix most often (sections 4.4 and 7).

## 2. Data

*Owner: Isbel.*

### 2.1 Source and target

- **Source:** `data/Train.csv` from the [Kaggle Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation) dataset (CC0 licence): 8,068 customers, 11 columns.
- **Target:** `Segmentation`, with four classes A, B, C and D. The dataset does not explain what each segment means.
- **Predictors (9):** `Gender`, `Ever_Married`, `Age`, `Graduated`, `Profession`, `Work_Experience`, `Spending_Score`, `Family_Size`, `Var_1`. `ID` is an identifier and is never used as a feature.

### 2.2 Why the original Kaggle `Test.csv` is not used

The Kaggle download also includes a `Test.csv` with labels. It is **excluded from the project** (D-006, D-012) because it cannot act as an independent test set:

- 2,332 of its 2,627 IDs also appear in `Train.csv`, often with different feature values (for example, ID 458989 has `Age` 36 in `Test.csv` and 42 in `Train.csv`).
- Among those shared IDs, the `Segmentation` label matches in only 30 % of cases.
- The class distribution differs (Train: D 28.1 %, A 24.4 %; Test: A 32.2 %, D 28.9 %).

### 2.3 Partition

`Train.csv` is split once into train, validation and test (70/15/15), stratified by `Segmentation`, with `random_state=42` (D-006, D-013). The three files are shared and read-only; every run checks their row counts, the absence of `ID` overlap and their SHA-256 (D-013 item 6).

| File | Rows | Use |
|---|---:|---|
| `data/train_70.csv` | 5,647 | EDA, fitting the preprocessing and the models, cross-validation |
| `data/val_15.csv` | 1,210 | Official overfitting check and comparison between models |
| `data/test_15.csv` | 1,211 | Final evaluation of the frozen model, once (US-12) |

Class shares in `train_70`: A 24.4 %, B 23.0 %, C 24.4 %, D 28.1 %. The classes are close to balanced.

### 2.4 Repeated profiles (D-009)

Some customers share the nine predictor values. They are kept (D-009) because, with nine mostly low-cardinality variables, identical profiles are expected and removing them would bias the sample. Section 4.4 measures how many there are and what ceiling they impose.

## 3. Methodology and Pipeline

*Owner: Isbel.*

### 3.1 Shared preprocessing Pipeline

All transformations live inside one scikit-learn Pipeline, fitted only on training data (inside each cross-validation fold, and on `train_70` for the final fit). `val_15` and `test_15` are only transformed (D-013 item 3).

| Step | Columns | Treatment | Decision |
|---|---|---|---|
| Numeric imputation | `Work_Experience`, `Family_Size` | Median (1.0 and 3.0 in `train_70`) plus a binary "was missing" indicator | D-011 |
| Categorical imputation | `Ever_Married`, `Graduated`, `Var_1` | Mode | D-011 |
| Categorical imputation | `Profession` | Constant level `Unknown` | D-011 |
| Binary encoding | `Ever_Married`, `Graduated`, `Gender` | One column each (`OneHotEncoder(drop="if_binary")`) | D-014 |
| Nominal encoding | `Profession`, `Var_1` | One-hot, one column per level | D-014 |
| Spending | `Spending_Score` | One-hot with three columns (the segment mix is not monotone across Low, Average and High) | D-014 |
| Scaling | All | `StandardScaler`, only in logistic regression and SVM | D-013 item 3, D-014 item 6 |

The transformed matrix has **28 columns** in `train_70`. Missing values in `train_70`: `Work_Experience` 9.97 %, `Family_Size` 4.32 %, `Ever_Married` 1.75 %, `Profession` 1.58 %, `Graduated` 0.94 %, `Var_1` 0.89 % (`reports/data_quality.md`). No row is removed.

### 3.2 Metric and overfitting criterion (D-010)

- **Primary metric:** macro-F1 on validation, so that the four segments weigh the same. Accuracy is reported for every model.
- **Overfitting:** `accuracy(train_70) − accuracy(val_15)` must be **below 5 percentage points**, as an absolute difference. The professor confirmed this reading on 2026-11-12.
- **Minimum reference:** a majority-class baseline (`DummyClassifier(strategy="most_frequent")`, which always predicts D).
- **Quality criterion ("good enough", D-010 item 5):** a model is acceptable if it clearly beats the baseline on validation macro-F1 and meets the overfitting limit.

### 3.3 Choosing each model's configuration (D-015)

Every model chose its final configuration with the same rule, approved by the team on 2026-11-17:

1. Candidate configurations are compared with 5-fold stratified cross-validation on `train_70`, passing the full Pipeline to every fold.
2. A configuration is admissible if its train − CV accuracy gap is below 5 points.
3. Among the admissible ones, those within one standard error of the best CV macro-F1 are treated as tied, and the one with the smallest gap is chosen.
4. If no configuration is admissible, the one with the smallest gap is chosen and the limitation is declared.
5. The chosen configuration is refitted on `train_70` and evaluated on `val_15`, where the official 5-point check applies.

`val_15` takes no part in choosing a configuration inside a model; it is used to check overfitting and to compare the four models.

### 3.4 Choosing the model (US-11)

Among the models that meet the overfitting limit on `val_15`, the one with the highest validation macro-F1 is chosen (D-010, Consequences, read as the comparison between models per D-015 item 9). The comparison table and the freezing tool are in `src/compare_models.py` (PR #72, merged).

> **Decision D-017 (Approved by Brian, 2026-11-17; Pedro, Brian and Isbel voted for it):** the frozen model is fitted on `train_70` only, not on `train_70 + val_15`, so its `val_15` figures stay held-out figures and the official check of D-010 keeps its meaning.
>
> **Done (US-11, PR #78):** XGBoost frozen on `train_70` (section 6.1). The choice is recorded as D-018, **Approved by Pedro** (reviewer of PR #78) on 2026-11-18.

### 3.5 Final evaluation (US-12)

The frozen model is evaluated on `test_15` **once**. The evaluation script (PR #73, merged) refuses to read `test_15` without an explicit flag.

## 4. Exploratory analysis

*Owner: Pedro. Source: `reports/eda_train70_sintesis.md` (US-06, merged) and the notebooks `02_`, `03_` and `04_eda_train70_*.ipynb`. All figures are computed on `train_70`.*

### 4.1 Which single variables separate the segments

Accuracy of a one-variable decision tree (5-fold CV on `train_70`; the majority class gives 0.2810):

| Variable | Accuracy | Variable | Accuracy |
|---|---:|---|---:|
| `Spending_Score` | 0.4059 | `Family_Size` | 0.3053 |
| `Age` | 0.3974 | `Var_1` | 0.3016 |
| `Ever_Married` | 0.3896 | `Gender` | 0.2810 |
| `Graduated` | 0.3733 | `Work_Experience` | 0.2810 |
| `Profession` | 0.3512 | | |

No single variable determines the segment; the model has to combine them. `Gender` and `Work_Experience` alone do not beat the baseline.

### 4.2 Main relationships

- **Age** orders the segments: median 29 years in D, 41 in A, 46 in B and 49 in C (eta² = 0.144). The distributions overlap (standard deviation about 15 years).
- **Marital status** separates D: 28.4 % ever married in D against 57–79 % in A, B and C (Cramér's V = 0.408, nulls counted in the denominator).
- **Spending** separates D from B and C: D is 86.8 % Low (V = 0.302). B and C have similar shares of High spending (20.6 % and 21.2 %).
- **Profession and spending** are strongly associated (V = 0.441): Executive (65.4 % High) and Lawyer (51.6 % High) are the only professions where High spending is the majority.
- **Every customer who has never married has Low spending** (2,284 customers; V = 0.669 between the two variables). Part of what one variable says is already said by the other.
- Missing values are informative: the customers with missing `Family_Size`, `Profession`, `Ever_Married` or `Work_Experience` are more often in D than the 28.1 % of the whole split.

### 4.3 Outliers and leakage

The numeric ranges are plausible (`Age` 18–89, `Work_Experience` 0–14, `Family_Size` 1–9) and no outlier is removed. No variable reproduces the segment deterministically, and `ID` is unrelated to it (Kruskal-Wallis p = 0.30).

### 4.4 Repeated and contradictory profiles

| Measure | Value |
|---|---:|
| Distinct profiles (9 predictors) | 5,246 of 5,647 rows |
| Repeated profiles | 322 (723 rows) |
| Profiles with more than one segment | 158 (365 rows, 6.5 %) |
| Rows that no model with these 9 predictors can classify correctly | 171 (3.0 %) |

The most frequent mixed pair is **B + C** (55 profiles), followed by A + B (30). These contradictions set a small error floor (3 %), so they do not explain the gap between the models (about 50–54 % accuracy) and a perfect classifier.

## 5. Models and validation results

*Owner: Brian. Sources: `results/svm.csv` (merged), `results/random_forest.csv` (PR #67, merged), `results/boosting.csv` (PR #65, merged), `results/logistic_regression.csv` (PR #66, merged).*

### 5.1 Models and configurations

| Model | Specific steps | Configurations compared | Selected configuration |
|---|---|---:|---|
| Logistic regression | `StandardScaler`, multinomial | 6 | `C=1`, L2, `class_weight="balanced"` |
| SVM | `StandardScaler`, `SVC` | 10 (baseline + 9) | RBF kernel, `C=1`, `gamma=0.01` |
| Random forest | — | 60 | 300 trees, `max_depth=6`, `min_samples_leaf=10`, `max_features=0.5` |
| XGBoost | — | 27 runs (26 candidates in the selection) | 300 trees, `max_depth=3`, `learning_rate=0.05`, `subsample=1.0`, `colsample_bytree=0.8`, `min_child_weight=5` (run `refine_n_estimators=300_learning_rate=0.05_min_child_weight=5`; `SELECTED_PARAMS` in `src/train_boosting.py`) |

For XGBoost, no configuration met the 5-point gap in cross-validation (smallest gap 6.19 points), so D-015 item 6 applies: the configuration with the smallest gap was chosen. It meets the official limit on `val_15` (3.33 points).

### 5.2 Baseline (default parameters) and selected configuration

Accuracy and macro-F1 on `train_70` and `val_15`; the gap is train − validation accuracy in points.

| Model | Version | Acc. train | Acc. val | Macro-F1 train | Macro-F1 val | Gap | Meets < 5 |
|---|---|---:|---:|---:|---:|---:|:---:|
| Majority class | — | 0.2810 | 0.2810 | 0.1097 | 0.1097 | 0.00 | — |
| Logistic regression | default | 0.5128 | 0.5058 | 0.4894 | 0.4797 | 0.71 | yes |
| Logistic regression | **selected** | 0.5123 | 0.4959 | 0.4991 | 0.4786 | 1.64 | yes |
| SVM | default | 0.5877 | 0.5240 | 0.5734 | 0.5063 | 6.38 | no |
| SVM | **selected** | 0.5413 | 0.5025 | 0.5279 | 0.4853 | 3.89 | yes |
| Random forest | default | 0.9683 | 0.4959 | 0.9675 | 0.4830 | 47.24 | no |
| Random forest | **selected** | 0.5438 | 0.5248 | 0.5321 | 0.5080 | 1.90 | yes |
| XGBoost | default | 0.6814 | 0.5314 | 0.6717 | 0.5162 | 15.00 | no |
| XGBoost | **selected** | 0.5762 | 0.5430 | 0.5608 | 0.5227 | 3.33 | yes |

The gaps are the values recorded in the `notes` of each run, computed before rounding the accuracies to four decimals.

Two readings:

- The default random forest and XGBoost memorise the training data (gaps of 47.24 and 15.00 points). Limiting tree depth and the minimum size of the leaves brings both below the limit.
- The default SVM has a higher validation macro-F1 than the selected one (0.5063 against 0.4853), but it fails the overfitting limit (6.38 points). The rule gives priority to a model that generalises over a slightly higher score.

### 5.3 Per-class results on validation (selected configurations)

Precision (P), recall (R) and F1 on `val_15`:

| Model | A (P / R / F1) | B (P / R / F1) | C (P / R / F1) | D (P / R / F1) |
|---|---|---|---|---|
| Logistic regression | 0.395 / 0.419 / 0.407 | 0.349 / 0.262 / 0.299 | 0.491 / 0.542 / 0.515 | 0.673 / 0.715 / 0.693 |
| SVM | 0.391 / 0.419 / 0.405 | 0.357 / 0.269 / 0.307 | 0.522 / 0.556 / 0.539 | 0.664 / 0.721 / 0.691 |
| Random forest | 0.442 / 0.399 / 0.419 | 0.381 / 0.333 / 0.356 | 0.537 / 0.566 / 0.551 | 0.662 / 0.756 / 0.706 |
| XGBoost | 0.462 / 0.412 / 0.436 | 0.425 / 0.326 / 0.369 | 0.546 / 0.600 / 0.572 | 0.654 / 0.785 / 0.714 |

The pattern is the same in the four models: D is recognised best, B worst. B has the lowest recall everywhere (0.26–0.33): most B customers are predicted as another segment.

### 5.4 Does the model predict with quality, and does it generalise?

Against the criterion of section 3.2:

- **Quality against the baseline:** the four selected models multiply the baseline macro-F1 by more than four (0.4786–0.5227 against 0.1097) and add 21–26 accuracy points (0.4959–0.5430 against 0.2810). They clearly beat it.
- **Generalisation:** the four meet the 5-point limit on `val_15` (gaps between 1.64 and 3.89 points).
- **Ranking on `val_15`:** XGBoost 0.5227 > random forest 0.5080 > SVM 0.4853 > logistic regression 0.4786 (macro-F1). The difference between the first two is small (0.0147) and has not been tested statistically.
- **Ceiling:** about half of the customers are classified correctly. Section 4.4 shows that contradictory profiles explain only 3 %; the rest reflects the limited information in nine variables (section 9).

> **Checked against the comparison table (2026-11-18):** `python -m src.compare_models --stage table` on `develop` gives the same accuracies, macro-F1 and per-class F1 as tables 5.2 and 5.3, and names XGBoost (`boosting`) as the model with the highest `val_15` macro-F1 (0.5227) among the 4 of 4 models with a gap below 5 points. Its gap column subtracts the accuracies already rounded to four decimals, so it shows 3.88 (SVM) and 3.32 (XGBoost) instead of 3.89 and 3.33; the result does not change.
>
> **Frozen in PR #78:** XGBoost on `train_70` (D-017); results in section 6.

## 6. Final model and test evaluation

*Owner: Brian. Sources: PR #78 (merged 2026-11-18), AI activity log A-029, `reports/*_test_15_20261118T092535Z.csv`, `reports/*_val_15.csv`.*

### 6.1 Frozen model

| Field | Value | Source |
|---|---|---|
| Model | XGBoost: highest `val_15` macro-F1 among the four models, all below the 5-point gap (section 5.4) | `results/model_comparison.csv` |
| Configuration | 300 trees, `max_depth=3`, `learning_rate=0.05`, `subsample=1.0`, `colsample_bytree=0.8`, `min_child_weight=5` (D-015 item 6) | `frozen_params` in the joblib file; `SELECTED_PARAMS` in `src/train_boosting.py` |
| Fitted on | `train_70` (5,647 rows), per D-017 | `trained_on`, `rows` in the joblib file |
| Preprocessing | Shared Pipeline of section 3.1 (D-011, D-014; 28 columns), wrapped in `FrozenPipeline` (`src/frozen.py`) so that it takes and returns the labels A–D | `src/compare_models.py --stage freeze --model boosting` |
| Random seed | 42 | `src/config.py` |
| Frozen on | 2026-11-18, PR #78 (`c6ce6c6` in `develop`); the `.joblib` file is not committed and is rebuilt with the command above; a rebuilt file can differ in a few predictions (section 9) | A-029 |
| Model file | `models/final_model.joblib`, SHA-256 `428e56ddcf3b1fa60c364bca2308e68ce4596cc30a121e62c98ce5492f817317`: the file evaluated on `test_15` and shared with the team | Computed on 2026-11-18 on Brian's copy (`sha256sum`) and on Rita's copy (`shasum -a 256`); both match |

> **D-018 (Approved by Pedro, 2026-11-18):** XGBoost frozen on `train_70` is the final model.

Its configuration was chosen by D-015 item 6 (no configuration met the 5-point gap in cross-validation, section 5.1); it meets the official limit on `val_15` (3.33 points in the recorded run).

**Validation figures of the frozen model.** The frozen model scores 0.5421 accuracy and 0.5222 macro-F1 on `val_15`, against 0.5430 and 0.5227 in the recorded boosting run of section 5.2: one row of 1,210 differs. A-029 reproduces the lower figure with the boosting module itself, so the wrapper is not the cause; the likely cause is run-to-run variation of XGBoost. Section 5 keeps the recorded run; this section uses the frozen model.

**Overfitting check of the frozen model (D-010).** On `train_70` the frozen model scores accuracy 0.5766 and macro-F1 0.5609, so its train − validation gap is **3.44 points** (computed before rounding), below the 5-point limit. Source: A-029, completed in PR #79.

### 6.2 Results on `test_15`

`test_15` (1,211 rows) was opened once, on 2026-11-18 at 09:25 UTC, with `python -m src.evaluate_final --model models/final_model.joblib --partition test_15 --allow-test`. Source: `reports/final_metrics_test_15_20261118T092535Z.csv`.

| | Accuracy | Macro-F1 |
|---|---:|---:|
| Frozen model on `test_15` | **0.5599** | **0.5456** |
| Same model on `val_15` | 0.5421 | 0.5222 |
| Test − validation (points) | +1.77 | +2.34 |
| Majority-class baseline on `test_15` | 0.2816 | 0.1099 |

The baseline row comes from the output of the same run, recorded in A-029 (PR #79); the script prints it but does not save it to a file.

Per class on `test_15`:

| Segment | Precision | Recall | F1 |
|---|---:|---:|---:|
| A | 0.484 | 0.456 | 0.470 |
| B | 0.484 | 0.385 | 0.429 |
| C | 0.570 | 0.608 | 0.588 |
| D | 0.648 | 0.751 | 0.696 |

### 6.3 Confusion matrix on `test_15`

Rows are the true segment, columns the predicted one. Sources: `reports/confusion_counts_test_15_20261118T092535Z.csv` and `reports/confusion_normalised_test_15_20261118T092535Z.csv`.

Counts:

| True \ Predicted | A | B | C | D | Total |
|---|---:|---:|---:|---:|---:|
| A | 135 | 51 | 42 | 68 | 296 |
| B | 54 | 107 | 87 | 30 | 278 |
| C | 26 | 49 | 180 | 41 | 296 |
| D | 64 | 14 | 7 | 256 | 341 |

Normalised by row (each row sums to 1; the diagonal is the recall of the segment):

| True \ Predicted | A | B | C | D |
|---|---:|---:|---:|---:|
| A | **0.456** | 0.172 | 0.142 | 0.230 |
| B | 0.194 | **0.385** | 0.313 | 0.108 |
| C | 0.088 | 0.166 | **0.608** | 0.139 |
| D | 0.188 | 0.041 | 0.021 | **0.751** |

Section 7 (US-14) reads which pairs are confused most.

### 6.4 Does the result hold on test?

- **Against validation:** test is +1.77 points of accuracy and +2.34 of macro-F1 above the frozen model's validation figures. There is no sign that the choice was tuned to `val_15`; with 1,211 rows, a difference of this size can come from sampling, so test is not read as an improvement.
- **Generalisation:** 0.5599 accuracy on unseen data is in line with validation; the frozen model's train − validation gap is 3.44 points (section 6.1), so it meets the overfitting limit.
- **Per class:** the pattern of section 5.3 holds. D is recognised best (recall 0.751) and B worst (recall 0.385).
- **Against the baseline:** on `test_15` the model doubles the baseline accuracy (0.5599 against 0.2816) and multiplies its macro-F1 by about five (0.5456 against 0.1099). It clearly beats it, which with the gap above meets the quality criterion of D-010 item 5.

### 6.5 Feature importance

Method: permutation importance of the **nine original variables** (each column is shuffled and the drop in macro-F1 is measured; 5 repeats, `random_state=42`). It is computed on `val_15`, not on `test_15`, as issue #29 asks. Source: `reports/feature_importance_val_15.csv`.

| Variable | Macro-F1 drop (mean) | SD |
|---|---:|---:|
| `Age` | 0.080 | 0.004 |
| `Profession` | 0.077 | 0.004 |
| `Spending_Score` | 0.054 | 0.004 |
| `Family_Size` | 0.029 | 0.007 |
| `Graduated` | 0.017 | 0.005 |
| `Gender` | 0.015 | 0.003 |
| `Work_Experience` | 0.013 | 0.004 |
| `Var_1` | 0.007 | 0.006 |
| `Ever_Married` | 0.006 | 0.002 |

How to read it:

- Importance is not causality: it says how much the model relies on a variable, not that the variable causes the segment.
- Overlapping variables share importance. `Ever_Married` and `Spending_Score` are strongly related (Cramér's V 0.669, section 4.2): `Ever_Married` ranks last although it has the highest Cramér's V with the segment in the EDA, which is consistent with `Spending_Score` and `Age` already carrying most of its information.
- Compared with the EDA (section 4.1): `Age` and `Spending_Score` rank high in both; `Profession` ranks higher in the model than as a single variable; `Gender` and `Work_Experience`, which add nothing on their own, have a small but non-zero importance.

## 7. Error analysis

*Owner: Pedro. Full analysis: `reports/error_analysis.md` (US-14, issue #32); this section summarises it.*

> **Partly pending (US-14).** The structure follows the acceptance criteria of issue #32. Sections 7.2 and 7.3 are copied from the US-12 run (section 6); 7.4 and 7.6 contrast them with the segment profiles of section 8.1 and the EDA of section 4; 7.5 and 7.7 are pending (US-14, PR #81). Explanations are hypotheses, not facts. The frozen model is not refitted or adjusted with anything found here.

### 7.1 Preview from validation and the EDA

Written before the test run; sections 7.2 and 7.3 check it:

- B is the weakest segment in every model (recall 0.26–0.33 on `val_15`, section 5.3).
- B and C are the pair most often mixed in the data (55 contradictory profiles, section 4.4) and they have similar profiles (section 8.1). *Hypothesis:* many B errors go to C, and some to A (B has the lowest recall in the four models). To be checked with the confusion matrix (US-12, US-14).

### 7.2 Weakest segments

From the per-class table of section 6.2:

| Segment | Precision | Recall | Reading |
|---|---:|---:|---|
| Lowest recall: B | 0.484 | 0.385 | Fewer than 4 in 10 B customers are recognised; B was also the weakest on validation |
| Lowest precision: A and B (tied at three decimals) | 0.484 / 0.484 | 0.456 / 0.385 | About half of the customers predicted as A or as B belong to another segment |

### 7.3 Most confused pairs

From the row-normalised confusion matrix of section 6.3 (share of the true segment predicted as the other one), largest off-diagonal cells first:

| True | Predicted as | Share of the true segment | Count |
|---|---|---:|---:|
| B | C | 0.313 | 87 |
| A | D | 0.230 | 68 |
| B | A | 0.194 | 54 |
| D | A | 0.188 | 64 |
| A | B | 0.172 | 51 |

Contrast with the data: the largest error, **B predicted as C**, matches the pair most often mixed in the data (B + C, 55 contradictory profiles, section 4.4), and B and A are confused in both directions, as the second mixed pair (A + B, 30) suggests. The preview of section 7.1 holds. **A and D are also confused in both directions** (A as D and D as A), a pair that section 4.4 does not list among the most mixed; why is for US-14.

### 7.4 Why: contrast with the segment profiles

For each confused pair of section 7.3, the traits of section 8.1 (`train_70`) that the two segments share or do not share. All explanations are *hypotheses*:

- **B and C (B predicted as C: 87, the largest error).** The two segments are close in every trait except spending: median age 46 and 49, ever married 73.7 % and 79.5 %, graduated 72.9 % and 81.7 %, Artist as the most frequent profession in both, and almost the same share of High spending (20.6 % and 21.2 %). Where they differ is Low spending (48.7 % in B, 33.6 % in C). *Hypothesis:* a B customer with Average or High spending has nothing left that separates it from C. It is also the pair most often mixed in the data (55 contradictory profiles, section 4.4), so part of this error cannot be removed with these nine variables.
- **A and D, in both directions (A as D: 68; D as A: 64).** They share their spending: most of their customers spend Low (69.1 % in A, 86.8 % in D). They differ in age (median 41 and 29), marital status (58.2 % and 29.0 % ever married), education (61.5 % and 37.8 % graduated) and profession (Artist and Healthcare). *Hypothesis:* a young, unmarried A customer with Low spending looks like D, and an older or married D customer looks like A. Section 4.4 does not list A + D among the most mixed pairs, so these errors are more likely to come from overlapping distributions than from identical profiles.
- **A and B, in both directions (B as A: 54; A as B: 51).** A is the "mixed profile", close to the average of all customers, and B lies between A and C on every trait: median age 41 and 46, ever married 58.2 % and 73.7 %, graduated 61.5 % and 72.9 %, Low spending 69.1 % and 48.7 %. *Hypothesis:* the differences are moderate on every variable and no single one separates the two segments (section 4.1), so customers near the middle are assigned to either. A + B is the second most mixed pair in the data (30 profiles, section 4.4).

### 7.5 Review of misclassified rows

> **Source: `val_15`.** The single test run (PR #78) did not save the prediction for each row, and opening `test_15` again is not allowed (sections 3.5 and 10.1), so the misclassified rows are reviewed on `val_15`, where the frozen model can be re-run. Its confusion matrix is in `reports/confusion_counts_val_15.csv`.

A sample of misclassified rows with their nine variables, true and predicted segment, grouped by the most confused pairs. The review describes what the rows have in common; it is not used to change the model.

| True | Predicted | Variables in common | Observation |
|---|---|---|---|
| … | … | … | … |

### 7.6 What data would help

Variables that are not in the dataset and could separate the confused segments (input for the business recommendation, section 8 and US-17): income, product (P1–P5) and vehicle type are named in the project brief and missing (section 9). Which of them would help each confused pair is a hypothesis:

- **B and C:** they differ mainly in spending, which the dataset only gives as three levels. Income or the amount actually spent, and the products bought (P1–P5), could separate a B customer with Average spending from a C customer.
- **A and D:** both spend Low. Income and vehicle type could tell whether the same low spending hides different capacities to spend.
- **A and B:** no single variable separates them today; the products bought could show whether they buy different things at similar spending levels.

None of these variables was measured, so their effect on the errors cannot be estimated with this dataset.

### 7.7 Performance by subgroup (optional)

Accuracy or recall by subgroup (for example age band, `Ever_Married` or `Spending_Score`), if time allows: …

## 8. Segments and business reading

*Owner: Rita. Source: `reports/segment_insights.md` and `reports/segment_profile_train_70.csv` (PR #69, merged, US-13 part 1), computed on `train_70`.*

### 8.1 Profile of each segment

Percentages exclude missing values from the denominator.

| | A | B | C | D |
|---|---:|---:|---:|---:|
| Customers in `train_70` | 1,380 | 1,301 | 1,379 | 1,587 |
| Median age | 41 | 46 | 49 | 29 |
| % ever married | 58.2 | 73.7 | 79.5 | 29.0 |
| % graduated | 61.5 | 72.9 | 81.7 | 37.8 |
| Most frequent profession | Artist (28.4 %) | Artist (41.1 %) | Artist (53.8 %) | Healthcare (43.2 %) |
| % High spending | 13.7 | 20.6 | 21.2 | 6.6 |
| % Low spending | 69.1 | 48.7 | 33.6 | 86.8 |

The names below are **team hypotheses** used to talk about the segments, not facts:

- **D, "young low spenders":** the largest and most distinct segment.
- **C, "mature graduates with the highest spending".**
- **B, "married graduates with medium spending":** similar to C with somewhat lower values.
- **A, "mixed profile":** close to the average of all customers.

### 8.2 Segment to prioritise

> **Approved rule (D-016, approved by Pedro in the review of PR #69, 2026-11-17):** prioritise the segment with the most High-spending customers in `train_70`.

C is the **provisional first priority** (292 High-spending customers, 34.2 % of all of them), and B is also a segment of interest (268, 31.4 %). `Spending_Score` is a proxy of customer value: the dataset has no income or revenue.

### 8.3 Campaigns

The campaign per segment that the app shows (US-15) is a **business hypothesis, not a model result**. The table is in `reports/segment_insights.md`, section 5, approved as business hypotheses in the review of PR #69 (Pedro, 2026-11-17).

### 8.4 Which variables matter

The frozen model relies most on `Age`, `Profession` and `Spending_Score` (permutation importance on `val_15`, section 6.5). Section 4 gives the descriptive evidence: spending, age and marital status separate D from the rest; no single variable separates B from C. Importance is not causality.

## 9. Limitations

- **Missing business variables.** The dataset has no income, products (P1 to P5) or vehicle type. The model cannot adapt a strategy to them; the recommendation is to collect them.
- **Segments without meaning.** A, B, C and D are not explained in the dataset; the names in section 8 are hypotheses.
- **Proxies.** `Spending_Score` and `Profession` stand in for customer value and income.
- **Information ceiling.** With nine variables, about half of the customers are classified correctly; 3 % of `train_70` belongs to contradictory profiles (D-009, section 4.4).
- **Overfitting cut in cross-validation.** D-015 applies the 5-point limit to the train − CV gap, which is larger by construction than the train − validation gap (each fold trains on 80 % of `train_70`). For XGBoost no configuration met it. The team kept 5 points for this delivery and recorded the issue as known technical debt (D-015, Evidence and limits).
- **Validation used for every configuration in three models.** The XGBoost, SVM and logistic regression runs evaluated all their configurations on `val_15`, not only the selected one. The choice was made with cross-validation, but `val_15` has been seen more than once.
- **Split by rows, not by profile.** The same profile can appear in `train_70` and in `val_15` or `test_15` (D-013). It affects the absolute accuracy, not the ranking, because all models use the same split.
- **Logistic regression results marked provisional.** Its results file still carries the note "PROVISIONAL (US-05 phase 2 not integrated)"; it applies D-011 and D-014 like the other models (28 columns).
- **Model file not versioned.** `models/final_model.joblib` is git-ignored, so the repository keeps the command that builds the model but not the file evaluated on `test_15` in PR #78. Rebuilding it, for example on another computer, can change a few predictions: on `val_15` the frozen model gets 656 of 1,210 rows right (diagonal of `reports/confusion_counts_val_15.csv`, accuracy 0.5421), while the recorded boosting run with the same configuration got 657 (accuracy 0.5430, `results/boosting.csv`; section 6.1). The figures of sections 6 and 7 hold only for the file frozen in PR #78, so the error analysis and the app must use that file, not a rebuilt one. Its SHA-256 (section 6.1) tells whether a copy is that file.
- **Association, not causality.** The EDA and the feature importance describe associations.

## 10. Reproducibility and sources

### 10.1 Environment

Python 3.12, packages pinned in `requirements.txt`; one seed for every stochastic step (`RANDOM_STATE = 42` in `src/config.py`). On macOS, XGBoost needs `brew install libomp` (README).

Model runs (each one appends its rows to `results/`; the logistic regression is run from `notebooks/03_modeling/01_logistic_regression.ipynb` with `src/model_logreg.py`):

```
python src/split_data.py --check                   # partitions match the committed files
python -m src.train_random_forest --stage tune     # random forest
python -m src.train_svm --stage tune               # SVM
python src/train_boosting.py --select              # XGBoost
```

Model choice, freeze and final evaluation (US-11, US-12). `src/compare_models.py` (PR #72) and `src/evaluate_final.py` (PR #73) are in `develop`:

```
python -m src.compare_models --stage table                                    # comparison table of the four models
python -m src.compare_models --stage freeze --model <name> --train-with train_70  # D-017; writes models/final_model.joblib
python -m src.evaluate_final --model models/final_model.joblib --partition val_15  # check + permutation importance
python -m src.evaluate_final --model models/final_model.joblib --partition test_15 --allow-test  # once (US-12)
```

`<name>` is one of `logistic_regression`, `svm`, `random_forest` or `boosting`; freezing needs the model's `SELECTED_PARAMS`. The test run refuses a second evaluation unless `--allow-test-rerun` is passed.

### 10.2 Sources of the figures

| Section | Figures | Source |
|---|---|---|
| 2.2 | `Test.csv` overlap and label agreement | D-006, D-012 (`docs/ai-usage/DECISION_LOG.md`) |
| 2.3 | Partition sizes and class shares | D-013; `reports/eda_train70_sintesis.md` |
| 3.1 | Missing values, medians | `reports/data_quality.md`, D-011 |
| 3.1 | 28 columns | D-014; checks in each model's tests |
| 4 | EDA | `reports/eda_train70_sintesis.md`, `reports/duplicates_train_70.csv`; `ID` vs segment test in `03_eda_train70_brian_outliers_fuga.ipynb` |
| 5 | Logistic regression | `results/logistic_regression.csv`, run 2026-11-17T11:15:23Z (PR #66, merged); majority class from the same file |
| 5 | SVM | `results/svm.csv`, runs 2026-11-17T10:10:48Z and 10:11:52Z |
| 5 | Random forest | `results/random_forest.csv`, tuning 2026-11-17T08:49:04Z and baseline 2026-11-17T10:12:28Z (PR #67, merged; the baseline was repeated later to add per-class precision and recall) |
| 5 | XGBoost | `results/boosting.csv`, baseline 2026-11-16T10:46:49Z and selection 2026-11-17T11:05:42Z (PR #65, merged) |
| 6 | Frozen model | `models/final_model.joblib` (not committed; rebuilt with `compare_models --stage freeze --model boosting`), PR #78, A-029 |
| 6, 7 | Test metrics and confusion matrices | `reports/final_metrics_test_15_20261118T092535Z.csv`, `reports/confusion_counts_test_15_20261118T092535Z.csv`, `reports/confusion_normalised_test_15_20261118T092535Z.csv` (single run, 2026-11-18 09:25 UTC, PR #78) |
| 6 | Frozen model on validation | `reports/final_metrics_val_15.csv`, `reports/confusion_counts_val_15.csv` (PR #78) |
| 6 | Feature importance | `reports/feature_importance_val_15.csv` (PR #78) |
| 6 | Baseline on `test_15`; frozen model on `train_70` (gap) | Output of the US-12 run and of the frozen model on `train_70`, recorded in A-029 (PR #79) |
| 7 | Error analysis | `reports/error_analysis.md` (pending US-14) |
| 8 | Segment profiles | `reports/segment_profile_train_70.csv`, run 2026-11-16 14:31 UTC (PR #69, merged) |

### 10.3 Decisions cited

D-006 and D-012 (dataset and test set), D-009 (repeated profiles), D-010 (metric and overfitting), D-011 (imputation), D-013 (shared partition), D-014 (encoding), D-015 (configuration selection), D-016 (segment prioritisation, approved), D-017 (data used to fit the frozen model, approved), D-018 (XGBoost as the final model, approved).
