# AI Activity Log

## Purpose

This document maintains a chronological record of significant AI-assisted work performed in the project.

Its purpose is to help team members understand previous activities, identify completed work and continue tasks without losing context.

## Logging Guidelines

- Record significant work sessions, not every individual interaction.
- Keep entries concise, factual and understandable.
- Distinguish between proposed, implemented and verified changes.
- Record actual commands and test results when relevant.
- Identify files created or modified.
- Never fabricate activities, results or completed tasks.
- Never include credentials, API keys, tokens or other secrets.
- Preserve previous entries. Never overwrite or delete historical records.

## Activity Records

### A-001 — Agent skills setup and project governance documentation

- **Date:** 2026-11-11
- **Agent:** opencode (GLM model), Skills CLI (`npx skills`)
- **Human owner:** Pending assignment (to be filled by the team)
- **Objective:** Evaluate, select and version shared AI agent skills for the Python/ML project, and establish project governance documentation (AGENTS.md + AI usage logs).
- **Activities:**
  - Searched and evaluated `mattpocock/skills` (38 skills found; global install of 2 TypeScript skills later ruled out as irrelevant).
  - Verified OpenCode 1.19.5 skill discovery from `.agents/skills` and the skills-lock.json restore procedure (`skills experimental_install --dry-run`).
  - Excluded unselected skills from the project installation; installed 4 approved skills project-locally (`tdd`, `diagnosing-bugs`, `code-review`, `research`); regenerated `skills-lock.json` (4 entries). Recorded as D-001 (Approved).
  - Created AGENTS.md (5 sections), restructured it from 208 to 65 lines per approved proposal, and added section 5 (Technical Standards and Reproducibility) with team-approved wording fixes.
  - Created `docs/ai-usage/DECISION_LOG.md` and `AI_ACTIVITY_LOG.md` templates; registered D-001.
- **Files:** Created: `AGENTS.md`, `.agents/skills/{tdd,diagnosing-bugs,code-review,research}/`, `skills-lock.json`, `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** `npx skills ls --json` (4 skills registered to OpenCode); dry-run restore from lock confirmed; `git status` inspected after each task.
- **Outcome:** Completed.
- **Pending tasks:** Skills `pr`, `to-spec`, `to-tickets` deferred pending tooling decisions; nothing committed yet (awaiting team authorization).

### A-002 — Git integration branch workflow documentation

- **Date:** 2026-11-12
- **Agent:** opencode (deepseek-v4.1-flash-free)
- **Human owner:** Pending assignment (to be filled by the team)
- **Objective:** Document the agreed Git workflow with an intermediate integration branch (`feature/* → develop → main`).
- **Activities:**
  - Inspected the current branch and working tree (`docs/project-setup`, clean).
  - Read `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md` and `docs/ai-usage/AI_ACTIVITY_LOG.md`.
  - Updated the Git Workflow section in `AGENTS.md` to describe `main`, `develop` and `feature/*`, keeping branch naming conventions and human approval rules.
  - Added a brief Git collaboration workflow section to `README.md`.
  - Registered D-008 (Status: Proposed) documenting the new flow and its relationship with D-007; D-007 was preserved unchanged.
- **Files:** Modified: `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** Cross-checked `AGENTS.md`, `README.md` and `DECISION_LOG.md` for contradictions; `git status` inspected (no Git operations performed).
- **Outcome:** Documentation updated. D-008 awaits team approval; branch protection rules for `develop` and `main` must be configured manually in GitHub.
- **Pending tasks:** Human approval of D-008; manual GitHub branch protection; commit/push pending explicit authorization.

### A-003 — Consolidation of Gitflow agreements into D-007

- **Date:** 2026-11-12
- **Agent:** opencode (deepseek-v4.1-flash-free)
- **Human owner:** Pending assignment (to be filled by the team)
- **Objective:** Consolidate the team's latest Gitflow and collaboration agreements into the existing approved decision D-007, and align the rest of the documentation.
- **Activities:**
  - Read the current `AGENTS.md`, `README.md`, `DECISION_LOG.md` and `AI_ACTIVITY_LOG.md`.
  - Expanded D-007 (keeping its date, status and prior technical agreements) with the branch flow, Squash Merge into `develop`, normal Merge Commit into `main`, same-day PR review, integration calendar and branch protection agreements.
  - Marked D-008 as `Consolidated into D-007`, preserving its date and traceability; added a `Consolidated` status definition.
  - Updated `AGENTS.md` §4 with merge strategies, PR review rules, milestone integrations and branch protection.
  - Updated the README Git Collaboration Workflow section with the flow, merge strategies and reviews.
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md`, `AGENTS.md`, `README.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** Cross-checked `AGENTS.md`, `README.md` and `DECISION_LOG.md` for contradictions; `git status` inspected (no Git operations performed).
- **Outcome:** Documentation consolidated. Branch protection must be configured manually in GitHub; no GitHub settings were changed.
- **Pending tasks:** Manual verification of GitHub plan limitations and branch protection; commit/push pending explicit authorization.

### A-004 — Task-branch scope clarification in Git workflow docs

- **Date:** 2026-11-12
- **Agent:** opencode (deepseek-v4.1-flash-free)
- **Human owner:** Pending assignment (to be filled by the team)
- **Objective:** Extend the documented Git rules from `feature/*` to all task branches (`fix/*`, `docs/*`, `refactor/*`).
- **Activities:**
  - Updated the Pull Requests rule in `AGENTS.md` to cover all task branches.
  - Updated the README Git Collaboration Workflow to refer to task branches in the Pull Requests section.
  - Aligned D-007 in `DECISION_LOG.md` with the same task-branch scope.
  - Verified the D-008 approval/consequences separation; the lines are already independent (the leading `+` seen in a diff is a diff marker, not file content).
- **Files:** Modified: `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** `git status` inspected; no Git write operations performed.
- **Outcome:** Documentation now consistently covers all task branches.
- **Pending tasks:** Commit/push pending explicit authorization.

### A-005 — Repository review, EDA review and test-set decision

- **Date:** 2026-11-11 / 2026-11-12
- **Note:** Originally recorded as A-002 on branch `docs/discard-external-test-csv`; renumbered to A-005 when merging `develop` (PR #41 had already used A-002–A-004).
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Review the repository setup and Pedro's EDA notebook; update the documentation after the team decided not to use `Test.csv`.
- **Activities:**
  - Reviewed AGENTS.md, AI usage logs, installed skills, `.gitignore` and git history (read-only).
  - Compared `Train.csv` and `Test.csv` with a Python `csv` script: 2,332 of 2,627 Test IDs also appear in Train with different values; class distributions differ.
  - Ran `git pull` on `main` (fast-forward to `75374d9`, PR #40).
  - Reviewed `01_eda_inicial.ipynb` on `origin/feature/eda-pedro` (read-only, not executed). Findings shared with the team: the 70/15/15 split described in the notebook is not in its code (analysis runs on all 8,068 rows); one code cell is stored as Markdown; one cell not executed; duplicated cells; out-of-order execution.
  - On human request, created branch `docs/discard-external-test-csv`, updated AGENTS.md (§1 data rules, §5 validation line) and README, and proposed D-006. Clarified with the team owner that an initial basic EDA on the full `Train.csv` is descriptive only, and reflected this in AGENTS.md and D-006.
  - Checked `Train.csv` for duplicates (Python `csv` script): 417 rows are exact duplicates of another row ignoring `ID`; 734 rows repeat another row's features. Further analysis (same script): 291 of 549 repeated profiles have different `Segmentation` labels and IDs of the same profile are far apart, so they were judged to be different customers with the same profile, not real duplicates. Rita Pereira agreed to keep them; recorded as D-009 (Proposed).
  - Reviewed PR #43 (`feature/eda-pedro`): verified with a Python `csv` script that `train_70`/`val_15`/`test_15` have 5,647/1,210/1,211 rows, no shared IDs, union equal to `Train.csv`, rows identical to the source and class proportions within ±0.06 points. Review comments drafted for the team (split cell skips regeneration when files exist; notebook not run from a clean kernel).
  - Merged `origin/develop` into `docs/discard-external-test-csv` to resolve the PR #42 conflict in this log (only conflicting file).
  - `git fetch --prune` (2026-11-12, before PR #41 was merged): at that time `origin/develop` pointed to the same commit as `main` (`75374d9`).
  - Addressed the PR #42 review: moved D-006 before D-007 in the Decision Log (it had been appended after D-008); clarified in D-006 and AGENTS.md that `Test.csv` stays in the repository but is not used; recorded the duplicates decision as D-009 (Proposed); updated the PR description.
- **Files:** Modified: `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** `git status` / `git diff` inspected; no code or tests to run.
- **Outcome:** Documentation changes implemented. D-006 and D-009 are Proposed (not approved).
- **Pending tasks:** Human approval of D-006 and D-009; review and merge PR #42; `requirements.txt` (assigned to Isbel); move the split to `src/` per D-007.

---

### A-006 — Initial EDA on Train.csv and 70/15/15 stratified data split

- **Date:** 2026-11-12
- **Agent:** Gemini
- **Human owner:** Pedro
- **Objective:** Perform initial exploratory data analysis on `data/Train.csv`, verify duplicate profiles, and generate reproducible stratified data splits (`train_70`, `val_15`, `test_15`) preserving raw missing values.
- **Activities:**
  - Configured local data ingestion from `data/Train.csv` (with on-demand `kagglehub` fallback), excluding Kaggle's external `Test.csv` (aligned with D-006).
  - Performed structural inspection, missing-value diagnosis, and univariate visualizations (target class balance, numerical distributions/boxplots, and categorical frequencies) across all 8,068 records.
  - Analyzed exact feature matches (`ID` and `Segmentation` excluded), confirming they represent distinct customers with identical profiles across different segments rather than true data duplicates.
  - Implemented reproducible stratified splitting (`random_state=42`, 70/15/15) exporting `train_70.csv`, `val_15.csv`, and `test_15.csv` with missing values intact for downstream `src/` pipeline processing.
- **Files:** Modified: `01_eda_inicial.ipynb`; Created: `data/train_70.csv`, `data/val_15.csv`, `data/test_15.csv`.
- **Verification:** Executed `Restart & Run All` in `01_eda_inicial.ipynb`; verified exact row counts (5,647 / 1,210 / 1,211), zero ID overlap across splits, preserved missing values, and class proportions within ±0.06%.
- **Outcome:** Completed and submitted via PR on branch `feature/eda-pedro`.
- **Pending tasks:** Migrate split generation logic from notebook to `src/` pipeline module (per D-007) and execute deep EDA/imputation rules exclusively on `train_70.csv`.

### A-007 — US-01: primary metric and overfitting criterion

- **Date:** 2026-11-12
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Document the proposed primary metric, overfitting criterion and minimum reference for US-01 (issue #8).
- **Activities:**
  - Read issue #8 (US-01) and the dependent user stories (US-07 to US-11) with `gh`.
  - Proposed macro-F1 as primary metric, accuracy also reported, equal error costs, both absolute and relative train/validation gaps until the professor confirms the criterion, and the majority-class baseline as minimum reference. Rita Pereira agreed with each point; the professor is being asked about the overfitting metric.
  - Recorded the proposal as D-010 (Proposed) on branch `feature/define-metric-overfitting-criterion` (created from `develop` at `3714435`).
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** No code executed. Baseline values in D-010 are analytical estimates (class D share in `val_15` from the recorded run in `01_eda_inicial.ipynb`), explicitly marked as not measured; they will be measured in US-11.
- **Outcome:** Documentation drafted; D-010 is Proposed.
- **Pending tasks:** Team approval of D-010 (PR #45).
- **Update (2026-11-12):** The professor answered (relayed by Rita Pereira) that, when using accuracy, overfitting is training accuracy minus validation accuracy. D-010 updated: pass/fail criterion is the absolute accuracy gap (< 5 percentage points); the macro-F1 gap stays informative. Added to PR #45 on the same branch.
- **Update (2026-11-12):** Alex suggested measuring the gap with `cross_validate`. The shared snippet had two bugs (`'acuracy'` instead of `'accuracy'`; train and CV scores read from the same, non-existent key, so the gap would always be 0); a corrected version using the full Pipeline and `StratifiedKFold(random_state=42)` was given to Rita Pereira (not executed: the Pipeline does not exist yet). Added to D-010 as item 6 (CV on `train_70` for tuning; official check stays train vs `val_15`).

---

<!-- Add new activities below using the same structure. Preserve previous records. -->
