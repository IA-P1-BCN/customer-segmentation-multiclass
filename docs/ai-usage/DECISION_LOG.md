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

---

<!-- Add new decisions below using the same structure. Preserve previous records. -->
