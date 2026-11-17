# Technical report: customer segmentation with multiclass classification (US-16)

**Status: draft (2026-11-17).** Rita Pereira integrates the document; each section names who writes or checks it (issue #36). Pedro reviews the whole report before delivery.

| Section | Owner | Status |
|---|---|---|
| 1. Summary | Rita | Draft; final figures pending US-11 and US-12 |
| 2. Data | Isbel | Draft from approved decisions |
| 3. Methodology and Pipeline | Isbel | Draft from approved decisions |
| 4. Exploratory analysis | Pedro | Draft from the merged US-06 synthesis |
| 5. Models and validation results | Brian | Draft from the recorded results of the four model PRs |
| 6. Final model and test evaluation | Brian | **Pending US-11 and US-12** |
| 7. Error analysis | Pedro | **Pending US-14**; validation-level preview only |
| 8. Segments and business reading | Rita | Draft from US-13 part 1 |
| 9. Limitations | Rita | Draft |
| 10. Reproducibility and sources | Rita | Draft |

**How to read the figures.** Every number comes from an executed run recorded in the repository (US-03, AGENTS.md section 5); section 10 lists the source of each one. The model results (sections 3 and 5) were checked against `develop` on 2026-11-17, after the four model PRs were merged. The segment figures (section 8) were checked against `develop` on 2026-11-17, after PR #69 was merged.

---

## 1. Summary

The project predicts the segment (A, B, C or D) of a customer from nine demographic and behavioural variables, using `Train.csv` from the Kaggle Customer Segmentation dataset. Four models were trained on the same shared partition and preprocessing: multinomial logistic regression, SVM, random forest and XGBoost. Each chose its configuration with the same rule (D-015).

On the validation split (`val_15`), the four selected configurations meet the overfitting limit (train − validation accuracy below 5 points) and clearly beat the majority-class baseline: macro-F1 between 0.4786 and 0.5227, against 0.1097 for the baseline. **XGBoost has the highest validation macro-F1 (0.5227, accuracy 0.5430).** The `val_15` figures of the four models are final; the choice of the frozen model and its test metrics are pending (US-11, US-12).

> **Fixed by D-017 (Approved by Brian, 2026-11-17):** the frozen model is fitted on `train_70` only.
>
> **Pending (US-11, US-12):** chosen model, test metrics, confusion matrix and feature importance.

All models find segment D easiest (F1 about 0.69–0.71) and segment B hardest (F1 about 0.30–0.37). B and C are the pair that the data themselves mix most often (section 4.4).

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

Among the models that meet the overfitting limit on `val_15`, the one with the highest validation macro-F1 is chosen (D-010, Consequences, read as the comparison between models per D-015 item 9). The comparison table and the freezing tool are in PR #72.

> **Decision D-017 (Approved by Brian, 2026-11-17; Pedro, Brian and Isbel voted for it):** the frozen model is fitted on `train_70` only, not on `train_70 + val_15`, so its `val_15` figures stay held-out figures and the official check of D-010 keeps its meaning.
>
> **Recorded in D-017 (Approved):** the frozen model is fitted on `train_70` only. **Pending (US-11):** run the freeze and record the choice of the final model.

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
| XGBoost | — | 27 runs (26 candidates in the selection) | `refine_n_estimators=300_learning_rate=0.05_min_child_weight=5` (refinement stage) |

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

> **Pending (US-11):** the `val_15` ranking is final for the four models. Confirm it with the comparison table of PR #72 and freeze the model (D-017: fitted on `train_70` only).

## 6. Final model and test evaluation

*Owner: Brian.*

> **Pending (US-11, US-12).** This section will contain the frozen model and its configuration, the data it was fitted on, accuracy, macro-F1 and per-class precision, recall and F1 on `test_15`, the confusion matrix in counts and normalised by row, the comparison with validation and with the baseline, and the feature importance with its method, grouped by original variable. Importance is not causality.

## 7. Error analysis

*Owner: Pedro.*

> **Pending (US-14).** This section will use the US-12 confusion matrix to identify the most confused pairs, contrast them with the segment profiles and review misclassified rows.

Preview from validation and the EDA, to be confirmed with the test results:

- B is the weakest segment in every model (recall 0.26–0.33 on `val_15`, section 5.3).
- B and C are the pair most often mixed in the data (55 contradictory profiles, section 4.4) and they have similar profiles (section 8.1). *Hypothesis:* many B errors go to C, and some to A (B has the lowest recall in the four models). To be checked with the confusion matrix (US-12, US-14).

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

> **Pending (US-12):** model-based feature importance. Until then, section 4 gives the descriptive evidence: spending, age and marital status separate D from the rest; no single variable separates B from C.

## 9. Limitations

- **Missing business variables.** The dataset has no income, products (P1 to P5) or vehicle type. The model cannot adapt a strategy to them; the recommendation is to collect them.
- **Segments without meaning.** A, B, C and D are not explained in the dataset; the names in section 8 are hypotheses.
- **Proxies.** `Spending_Score` and `Profession` stand in for customer value and income.
- **Information ceiling.** With nine variables, about half of the customers are classified correctly; 3 % of `train_70` belongs to contradictory profiles (D-009, section 4.4).
- **Overfitting cut in cross-validation.** D-015 applies the 5-point limit to the train − CV gap, which is larger by construction than the train − validation gap (each fold trains on 80 % of `train_70`). For XGBoost no configuration met it. The team kept 5 points for this delivery and recorded the issue as known technical debt (D-015, Evidence and limits).
- **Validation used for every configuration in three models.** The XGBoost, SVM and logistic regression runs evaluated all their configurations on `val_15`, not only the selected one. The choice was made with cross-validation, but `val_15` has been seen more than once.
- **Split by rows, not by profile.** The same profile can appear in `train_70` and in `val_15` or `test_15` (D-013). It affects the absolute accuracy, not the ranking, because all models use the same split.
- **Logistic regression results marked provisional.** Its results file still carries the note "PROVISIONAL (US-05 phase 2 not integrated)"; it applies D-011 and D-014 like the other models (28 columns).
- **Association, not causality.** The EDA and the feature importance describe associations.

## 10. Reproducibility and sources

### 10.1 Environment

Python 3.12, packages pinned in `requirements.txt`; one seed for every stochastic step (`RANDOM_STATE = 42` in `src/config.py`). On macOS, XGBoost needs `brew install libomp` (README).

```
python src/split_data.py --check                   # partitions match the committed files
python -m src.train_random_forest --stage tune     # random forest
python -m src.train_svm --stage tune               # SVM
python src/train_boosting.py --select              # XGBoost
```

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
| 8 | Segment profiles | `reports/segment_profile_train_70.csv`, run 2026-11-16 14:31 UTC (PR #69, merged) |

### 10.3 Decisions cited

D-006 and D-012 (dataset and test set), D-009 (repeated profiles), D-010 (metric and overfitting), D-011 (imputation), D-013 (shared partition), D-014 (encoding), D-015 (configuration selection), D-016 (segment prioritisation, approved), D-017 (data used to fit the frozen model, approved).
