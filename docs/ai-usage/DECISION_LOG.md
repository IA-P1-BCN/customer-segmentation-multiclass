# Decision Log

## Purpose

This document records significant project decisions to maintain transparency, consistency and shared context across the team and its AI agents.

Only decisions that affect the project's objectives, methodology, architecture, tools or development workflow should be recorded.

Routine tasks, minor code changes and temporary troubleshooting do not require entries.

## Decision Status

- **Proposed:** Suggested but not yet approved.
- **Approved:** Explicitly approved by a human team member.
- **Rejected:** Reviewed and explicitly rejected by a human team member.
- **Consolidated:** Agreements merged into another decision record; the record is retained for traceability.

AI agents can propose and document decisions, but cannot approve or reject them.

## Decision Records

### D-001 — Selection of shared AI agent skills

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Tools
- **Context:** The team needed a shared set of AI agent skills relevant to the Python and Machine Learning project.
- **Alternatives:** Install all available skills, select only project-relevant skills, or rely on global installations.
- **Recommendation:** Maintain a small, project-specific set of shared skills.
- **Decision:** Install and version `tdd`, `diagnosing-bugs`, `code-review` and `research` in `.agents/skills/`, with `skills-lock.json`.
- **Approval:** Explicitly approved by a human team member.
- **Consequences:** All team members can access the same skills after cloning the repository. The skills can be restored and validated using the Skills CLI.

### D-002 — Discard `to-tickets` skill

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Tools
- **Context:** Pending-skill evaluation. `to-tickets` turns plans or conversations into tickets published to a configured tracker (description captured verbatim before pruning; full body not re-verified locally).
- **Alternatives:** Install `to-tickets`, or rely on the team's existing task-management workflow.
- **Recommendation:** Discard the skill: it would duplicate task management the team already handles.
- **Decision:** **Discarded.** The team uses GitHub Projects to manage tasks, so this skill would be redundant.
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** `to-tickets` is not installed in the project and will not be reconsidered unless the team's task-management workflow changes.

### D-003 — Discard `to-spec` skill (for now)

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Tools
- **Context:** Pending-skill evaluation. `to-spec` synthesizes the current conversation into a spec and publishes it to the project issue tracker (description captured verbatim before pruning; full body not re-verified locally). Its publish step depends on a tracker and spec workflow that the team has not defined yet (the `setup-matt-pocock-skills` configuration that would provide it was discarded in D-001's selection process).
- **Alternatives:** Install `to-spec`, defer it until a tracker is defined, or discard it.
- **Recommendation:** Discard for now: without a defined tracker and spec flow the skill cannot operate as intended, and publishing to an external tracker would need explicit guardrails.
- **Decision:** **Discarded for now.** It depends on a spec-publication flow and tracker that the team has not defined yet.
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** `to-spec` is not installed in the project. It may be re-evaluated with its full SKILL.md if the team later defines an issue tracker and a specification workflow.

### D-004 — Defer `pr` skill

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Tools
- **Context:** Pending-skill evaluation. `pr` is used when writing a PR body (description captured verbatim before pruning; full body not re-verified locally, since the skill was excluded from the project installation and no longer exists on disk). It shows potential utility for drafting Pull Request descriptions, which is valuable for the team's GitHub workflow, but installing it without reading its full instructions was rejected to avoid unverified content.
- **Alternatives:** Install `pr` now based on its description alone, discard it, or defer it until its full content can be inspected.
- **Recommendation:** Defer: useful but not verifiable locally; re-evaluate at the first real Pull Request, when there is both need and context to inspect the complete SKILL.md.
- **Decision:** **Deferred.** Re-evaluated when the team reaches its first Pull Request; any installation will follow a full inspection of its content.
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** `pr` remains uninstalled. The project keeps a pending task to inspect and re-evaluate `pr` at the first PR milestone.

### D-005 — Defer OpenSpec

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Tools
- **Context:** Evaluation of whether to incorporate OpenSpec (a spec-driven development tool [unverified locally]) into the shared project environment. The analysis was based exclusively on local project files, distinguishing verified facts from unverified assumptions.
- **Alternatives:** Install OpenSpec now, postpone it with a re-evaluation trigger, or discard it permanently.
- **Recommendation:** Postpone: the existing environment already covers current needs (governance, decision log, activity log, GitHub workflow, 4 installed skills), and formal specification management would add complexity before EDA. The team had already discarded spec/tracker flows (D-002, D-003).
- **Decision:** **Deferred.** OpenSpec will not be incorporated in the current phase.
- **Justification:** The existing environment covers current needs; OpenSpec would add unnecessary complexity and maintenance.
- **Reevaluation trigger:** When development of the prediction application begins, or when changes are made on stable code.
- **Verification note:** The functionalities attributed to OpenSpec during the analysis were not verified locally (no external search was performed and nothing was installed or downloaded).
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** No `openspec/` structure or tooling is added. The decision is revisited at the reevaluation trigger; nothing needs maintenance in the meantime.

### D-006 — Discard external `Test.csv`; split `Train.csv` 70/15/15

- **Date:** 2026-11-12
- **Status:** Approved
- **Area:** Methodology / Data Management
- **Context:** AGENTS.md and the README described `Test.csv` as the project's separate test set. A local check (Python `csv` module, run 2026-11-11 by Claude Code) found that `Test.csv` has labels, but 2,332 of its 2,627 IDs also appear in `Train.csv` (8,068 rows) with different feature values (e.g. ID 458989: `Age` 36 in Test vs 42 in Train) and only 707 shared IDs keep the same `Segmentation` label. Class distribution also differs (Train: D 28.1 %, A 24.4 %; Test: A 32.2 %, D 28.9 %). The team had independently decided to split `Train.csv` directly (EDA work in `feature/eda-pedro`).
- **Alternatives:** (1) Use `Test.csv` as the final test set; (2) use `Test.csv` after removing overlapping IDs (only 295 rows left); (3) discard `Test.csv` and split `Train.csv` into train / validation / test.
- **Recommendation:** Option 3. Overlapping customers with altered records make `Test.csv` unreliable as an independent test set, and option 2 leaves too few rows for a robust evaluation.
- **Decision:** Do not use `Test.csv`. Split `Train.csv` once into train / validation / test (70/15/15), stratified by `Segmentation`, `random_state=42`. A first basic EDA on the full `Train.csv` (structure, types, nulls) precedes the split and is descriptive only; the full EDA, modeling decisions and all fitted preprocessing use only the train split; the test split is used only for the final evaluation. `ID` is never used as a feature. `Test.csv` stays versioned in the repository (CC0, per D-007) for traceability, but it is not used for training, validation or evaluation.
- **Approval:** Approved by Isbel, 2026-11-12.
- **Consequences:** AGENTS.md (§1, §5) and README updated accordingly. The split produces three new files in `data/` (train, validation and test), which every member uses instead of `Test.csv`. The split must be implemented reproducibly (shared code under `src/`, per D-007) so every member works with the same partitions. The new file names must not differ from `Train.csv`/`Test.csv` only by letter case (e.g. avoid `test.csv`): on case-insensitive file systems (macOS, Windows) they would overwrite the originals.

### D-007 — Collaborative workflow and dataset management

- **Date:** 2026-11-11
- **Last updated:** 2026-11-12 — Gitflow agreements, merge strategies, integration calendar and branch protection consolidated into this record.
- **Status:** Approved
- **Area:** Workflow / Data Management
- **Context:** The team needed to define how members collaborate during EDA, preprocessing and model development, whether the Kaggle dataset files can be kept in the repository, and which Gitflow and integration rules govern collaboration.
- **Decision:**
  1. **Git workflow:**
     - All task branches (`feature/*`, `fix/*`, `docs/*` and `refactor/*`) are created from `develop`.
     - Pull Requests from all task branches go exclusively to `develop`.
     - All task-branch Pull Requests are integrated with **Squash Merge**.
     - `develop` is the integration branch for joint testing.
     - When a milestone is validated, a Pull Request from `develop` to `main` is opened.
     - The integration of `develop` into `main` uses a **normal Merge Commit** (not Squash Merge or Rebase).
     - No direct commits are allowed on `develop` or `main`.
     - Each Pull Request must be small, specific and reviewed by another team member the same day.
  2. **Integration calendar:**
     - Friday, November 13: integration with the frozen model.
     - Monday, November 16: integration and validation.
     - Tuesday, November 17: last stable integration before delivery.
  3. **EDA:** each member explores independently. The EDA lead owns `01_eda.ipynb` and integrates relevant findings into the final notebook.
  4. **Notebooks:** each notebook has one designated owner. No simultaneous editing by multiple members.
  5. **Preprocessing and data split:** implemented in a shared Python Pipeline under `src/`, ensuring consistent processing across models.
  6. **Model experiments:** each member maintains their own model notebook, imports the shared Pipeline and records metrics in `results/` using a common format.
  7. **Dataset:** retain `Train.csv` and `Test.csv` in the repository. The Kaggle dataset is licensed under CC0, allowing redistribution. No changes to `.gitignore` are required.
  8. **Branch protection:** the team will attempt to require Pull Requests and at least one approval on `main` and `develop`. If the repository plan or configuration does not allow these protections, the rules must remain explicitly documented in `AGENTS.md` and be honored by team agreement. Plan limitations must be checked manually and are not assumed.
- **Dataset license note:** the CC0 license of the Kaggle dataset was confirmed by human review on Kaggle.
- **Documentation:** add the Kaggle dataset source and Analytics Vidhya reference to the README.
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** The team follows the `feature/* → develop → main` workflow with Squash Merge into `develop`, a normal Merge Commit into `main`, small same-day-reviewed Pull Requests, scheduled milestone integrations and single-owner notebooks with a shared preprocessing Pipeline. `Train.csv` and `Test.csv` remain versioned in the repository under the confirmed CC0 license, with no `.gitignore` changes.

### D-008 — Integration branch `develop` in the Git workflow

- **Date:** 2026-11-12
- **Status:** Consolidated into D-007
- **Area:** Workflow
- **Consolidation:** Its Gitflow agreements have been consolidated into D-007 (updated 2026-11-12). This record is retained for traceability and its date is preserved.
- **Context:** D-007 established that changes reach `main` exclusively through reviewed Pull Requests, but it did not define an intermediate integration stage. With several members developing features in parallel, integrating every feature directly into the stable branch made joint testing and release preparation harder.
- **Alternatives:**
  1. Keep the previous flow: `feature/*` PRs integrated directly into `main` (D-007).
  2. Adopt an intermediate integration branch: `feature/* → develop → main`.
  3. Integrate through long-lived release branches.
- **Recommendation:** Adopt an intermediate integration branch (`develop`): it isolates the stable branch from work in progress, allows joint testing of completed features and keeps `main` reserved for validated versions.
- **Decision:** Adopt the workflow `feature/* → develop → main`.
  1. `main` is the stable branch and only receives integrated, tested and approved versions.
  2. `develop` is the integration branch; it receives finished features and enables joint testing before preparing a release.
  3. `feature/*` branches are created from `develop`, where each member develops their task.
  4. `feature/*` branches open Pull Requests into `develop`, and each PR must be reviewed by another team member.
  5. Direct commits to `develop` and `main` are not allowed.
  6. Once `develop` is validated, a Pull Request is opened into `main`.
- **Relationship with D-007:** Its Gitflow agreements were consolidated into D-007, which is now the authoritative record for the workflow. D-007 also preserves its original agreements on EDA ownership, single-owner notebooks, shared preprocessing Pipeline, model experiment conventions and dataset management.
- **Approval:** Consolidated into D-007, which is Approved by a human team member (2026-11-11).
- **Consequences:** All feature work is integrated and validated in `develop` before reaching `main`. This adds one integration step and requires branch protection rules for both `develop` and `main` in GitHub.

### D-009 — Keep rows with identical feature profiles

- **Date:** 2026-11-12
- **Status:** Approved
- **Area:** Methodology / Data Management
- **Context:** In `Train.csv`, 1,283 rows (15.9 %) share all predictor values (ignoring `ID`) with at least one other row, across 549 profiles; removing them would drop 734 rows (417 if the label must also match). After the D-006 split, 82 rows of `val_15` and 78 of `test_15` have an exact copy in `train_70`. Checked with a Python `csv` script (Claude Code, 2026-11-12): 291 of the 549 profiles have different `Segmentation` labels, IDs of the same profile are far apart (only 7 pairs within 5 IDs), and the most repeated profiles are the most common ones in the dataset (e.g. young unmarried men in Healthcare with `Spending_Score` Low). With 9 mostly low-cardinality features, identical profiles are expected.
- **Alternatives:** (1) Remove exact duplicates before the split; (2) keep all rows; (3) group identical profiles so they fall in the same split.
- **Recommendation:** Option 2. The rows are most likely different customers with the same profile, not repeated records: removing them would discard real customers and distort the frequency of common profiles. Identical profiles across splits are not leakage, since new customers in production will also match profiles seen in training.
- **Decision:** Keep all rows; the D-006 split is not changed. Identical profiles with different labels set a ceiling on achievable accuracy and should be mentioned when reporting model performance. Pedro documents the analysis in `01_eda_inicial.ipynb` so the figures come from an executed run.
- **Approval:** Approved by Isbel, 2026-11-12.
- **Consequences:** No deduplication step in the Pipeline. `train_70`, `val_15` and `test_15` are used as generated in PR #43.

### D-010 — Primary metric, overfitting criterion and minimum reference (US-01)

- **Date:** 2026-11-12
- **Status:** Approved
- **Area:** Methodology / Evaluation
- **Context:** The four models (US-07 to US-10) need a single metric and a shared way of measuring overfitting to be comparable. The briefing requires overfitting below 5 % between training and validation, but does not state on which metric it is measured or whether the difference is absolute or relative. Classes are close to balanced (A 24.4 %, B 23.0 %, C 24.4 %, D 28.1 % in `train_70`, per the run in `01_eda_inicial.ipynb`). Per D-009, customers with identical profiles belong to different segments, which caps the achievable performance.
- **Alternatives:** (1) Accuracy as the only metric; (2) macro-F1 as the primary metric, with accuracy also reported; (3) weighted-F1.
- **Recommendation:** Option 2. Macro-F1 gives the four segments equal weight, so a model cannot look good by favouring the largest class (D); accuracy is kept because it is easy to explain in the business presentation. Weighted-F1 adds little with balanced classes.
- **Decision (proposed):**
  1. **Primary metric:** macro-F1 on validation. Accuracy is also reported for every model.
  2. **Error costs:** all segments and all errors weigh the same; no misclassification is considered more costly than another.
  3. **Overfitting:** the briefing limit (< 5 % between train and validation) is checked on **accuracy as an absolute difference**: `accuracy(train) − accuracy(validation) < 5 percentage points` (e.g. 65 % → 60 % is exactly 5 points and does not meet the limit). This follows the professor's answer (see below). The train − validation gap in macro-F1 is also reported for information, but it is not the pass/fail criterion.
  4. **Minimum reference:** every model must beat the majority-class baseline (`DummyClassifier(strategy="most_frequent")`, which always predicts D). Expected values on `val_15`: accuracy ≈ 28.1 % (share of D) and macro-F1 ≈ 0.11 (F1 of D ≈ 0.44, the other classes 0). **These are analytical estimates, not measured results**; the actual values are measured and recorded in US-11, and this item is then updated with the executed results.
  5. **Good enough:** a model is acceptable if it clearly beats the baseline on validation macro-F1 and meets the overfitting limit. Results are reported together with the ceiling described in D-009 (identical profiles with different segments).
  6. **Hyperparameter tuning with cross-validation (suggested by Alex):** during the improvement phase (US-07 to US-10), configurations are compared with 5-fold stratified cross-validation on `train_70` (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`), passing the **full Pipeline** (preprocessing + model) to `cross_validate` so that imputation and encoding are fitted inside each fold. Each configuration records mean accuracy and macro-F1 on the CV folds (with standard deviation) and the train − CV accuracy gap. This gives a more stable estimate than a single validation split and avoids tuning many configurations against `val_15`. The **official** overfitting check and the model comparison in US-11 remain train vs `val_15` (item 3), as stated by the professor.
- **Question to the professor:** Is the < 5 % overfitting limit measured on accuracy or on another metric (e.g. macro-F1), and is it an absolute difference in percentage points or a relative difference? Asked by Rita Pereira, 2026-11-12.
- **Professor's answer (2026-11-12, relayed by Rita Pereira):** when using accuracy, overfitting is measured by subtracting the validation accuracy from the training accuracy (absolute difference). The answer does not require a different metric, so the team applies it on accuracy.
- **Approval:** Approved by Brian, 2026-11-12.
- **Consequences:** US-07 to US-11 record accuracy and macro-F1 on train and validation, the accuracy gap in percentage points (pass/fail: < 5) and the macro-F1 gap (informative), plus per-class precision, recall and F1 on validation. Models are selected by validation macro-F1 among those that meet the accuracy-gap limit. During tuning, each configuration also records its 5-fold CV results on `train_70` (item 6).

### D-011 - Missing-value diagnosis and imputation strategy (US-04)

- **Date:** 2026-11-12
- **Status:** Proposed
- **Area:** Preprocessing / Data quality
- **Context:** US-04 requires a missing-value table per variable on the train split and an agreed imputation strategy for the Pipeline (US-05), with statistics computed only from `train_70`. Run of `src/data_quality.py` (opencode, 2026-11-12, Python 3.12.3, pandas 3.1.1) on `data/train_70.csv` (5,647 rows): `Work_Experience` 563 (9.97 %), `Family_Size` 244 (4.32 %), `Ever_Married` 99 (1.75 %), `Profession` 89 (1.58 %), `Graduated` 53 (0.94 %) and `Var_1` 50 (0.89 %); `ID`, `Gender`, `Age`, `Spending_Score` and `Segmentation` have no missing values. No duplicated `ID` in `Train.csv` (8,068 unique of 8,068 rows). Evidence per variable in `reports/data_quality.md`.
- **Alternatives:** (1) Drop every row with a missing value, which removes ~16 % of `train_70` and biases the sample towards customers who answered every field; (2) impute only with median/mode and no indicators; (3) median/mode plus missing indicators and an explicit `Unknown` level; (4) model-based imputation (KNN, iterative), which adds complexity and cost for a small share of missing data.
- **Recommendation:** Option 3. It keeps all customers, is cheap and explainable, and does not fabricate values where the mode is unreliable. Numeric variables with high missingness (`Work_Experience`, `Family_Size`) are right-skewed or small-range, so the median is robust; the missing indicators preserve the signal contained in the absence itself. `Profession` has 9 categories and a mode of only 31.4 % (`Artist`), so imputing `Artist` would invent a profession; an `Unknown` level is more honest and the encoder handles it natively. The remaining categorical variables are binary or heavily dominated by the mode (58.8 %, 62.4 % and 66.0 %), where the mode introduces little bias.
- **Decision (proposed):**
  1. `Work_Experience`: median (1.0) + binary indicator `Work_Experience_was_missing`.
  2. `Family_Size`: median (3.0) + binary indicator `Family_Size_was_missing`.
  3. `Ever_Married`: mode (`Yes`).
  4. `Graduated`: mode (`Yes`).
  5. `Var_1`: mode (`Cat_6`).
  6. `Profession`: constant category `Unknown`.
  7. Variables without missing values (`ID`, `Gender`, `Age`, `Spending_Score`) and the target `Segmentation`: no imputation; `ID` is never a feature.
  8. All statistics are fitted on `train_70` inside the Pipeline (`SimpleImputer` / `Pipeline`, inside each cross-validation fold). `val_15` and `test_15` are transformed with the values learned from train, never used to compute them.
- **Approval:** Pending team approval.
- **Consequences:** US-05 implements the strategy in the preprocessing Pipeline; no row is removed by missing values, so `train_70` keeps its 5,647 rows. The optional comparison of imputing vs dropping rows (US-04 extra) is not done now and can be added on validation if time allows.

---

<!-- Add new decisions below using the same structure. Preserve previous records. -->
