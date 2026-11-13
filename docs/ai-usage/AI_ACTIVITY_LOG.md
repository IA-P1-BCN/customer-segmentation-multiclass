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
- **Update (2026-11-12, status check):** D-006 and D-009 were approved by Isbel and integrated into `develop` with PR #42 (`d81aa03`, merged with a merge commit instead of Squash Merge; see A-008). Still pending and owned by other members: `requirements.txt` (US-03, Isbel) and moving the split to `src/` (D-007).

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
  - Proposed macro-F1 as primary metric, accuracy also reported, equal error costs, both absolute and relative train/validation gaps until the professor confirms the criterion, and the majority-class baseline as minimum reference. Rita Pereira agreed with each point; the professor is being asked about the overfitting metric. *(Initial proposal: the absolute + relative gaps were superseded by the professor's answer, which set the criterion as the absolute accuracy gap; see the first update below.)*
  - Recorded the proposal as D-010 (Proposed) on branch `feature/define-metric-overfitting-criterion` (created from `develop` at `3714435`).
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** No code executed. Baseline values in D-010 are analytical estimates (class D share in `val_15` from the recorded run in `01_eda_inicial.ipynb`), explicitly marked as not measured; they will be measured in US-11.
- **Outcome:** Documentation drafted; D-010 is Proposed.
- **Pending tasks:** Team approval of D-010 (PR #45).
- **Update (2026-11-12):** The professor answered (relayed by Rita Pereira) that, when using accuracy, overfitting is training accuracy minus validation accuracy. D-010 updated: pass/fail criterion is the absolute accuracy gap (< 5 percentage points); the macro-F1 gap stays informative. Added to PR #45 on the same branch.
- **Update (2026-11-12):** Alex suggested measuring the gap with `cross_validate`. The shared snippet had two bugs (`'acuracy'` instead of `'accuracy'`; train and CV scores read from the same, non-existent key, so the gap would always be 0); a corrected version using the full Pipeline and `StratifiedKFold(random_state=42)` was given to Rita Pereira (not executed: the Pipeline does not exist yet). Added to D-010 as item 6 (CV on `train_70` for tuning; official check stays train vs `val_15`).
- **Update (2026-11-12, status check):** D-010 was approved by Brian (his commits on the PR branch) and integrated into `develop` with PR #45 (Squash Merge, `559624c`). Issue #8 (US-01) closed as completed. Nothing pending for this activity; the baseline estimates in D-010 item 4 are still to be replaced with measured values in US-11.

### A-008 — Status check of Rita's deliverables against AGENTS.md

- **Date:** 2026-11-12
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Following Isbel's request to the team, check that Rita's deliverables follow AGENTS.md, that logs reflect the current state, and that no required changes remain outside `develop`.
- **Activities:**
  - Checked how PRs #42–#46 were merged (`gh api .../pulls/<n>`, `git log --first-parent origin/develop`).
  - Findings:
    - PR #42 (Rita's; merged by Brian, `d81aa03`) and PR #43 (Pedro's; merged by Rita, `5eeb450`) were integrated with a **merge commit instead of Squash Merge**, contrary to AGENTS.md §4. Not reverted: fixing it would require rewriting `develop` history. Recorded here for traceability.
    - PRs #44 and #45 were integrated with Squash Merge, as required.
    - PR #46 (Pedro's notebook rerun from a clean kernel, commit `871585e`) was **closed without merging by mistake** from Rita's account at 15:48 while she was trying to merge PR #45. Rita reopened it and integrated it with Squash Merge (`24af72b`, approved by Rita before the merge).
    - A-005 and A-007 still described D-006, D-009 and D-010 as pending; status updates added above (previous text preserved).
    - Issue #8 (US-01) was still open after PR #45; closed as completed with a comment linking PR #45.
  - Context noted for the team: `develop` requires approval of the most recent push; when a reviewer pushes to a PR branch (as happened in PR #45), another member must approve afterwards.
- **Files:** Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** Merge type of each PR checked through the GitHub API (single squash commit vs merge commit on `develop`); issue #8 state checked after closing.
- **Outcome:** Rita's deliverables are integrated in `develop` and the logs reflect their current status. The two non-squash merges remain in history as documented exceptions.
- **Pending tasks:** None for Rita's deliverables. Items owned by other members (Isbel's list): centralised seed and pinned dependencies (US-03), split logic moved to `src/` (D-007), duplicated profile analysis in `01_eda_inicial.ipynb` (cells 3 and 5).

---

### A-009 - Project Python environment and activity-log alignment

- **Date:** 2026-11-12
- **Agent:** opencode (DeepSeek V4.1 Flash Free)
- **Human owner:** Pedro
- **Objective:** Prepare a reproducible Python environment for the project and align the activity log with the integration branch `develop`.
- **Activities:**
  - Reviewed `AGENTS.md`, `DECISION_LOG.md` and `AI_ACTIVITY_LOG.md` before acting; work done on branch `feature/eda-pedro`.
  - Inspected the shared environment `F:\venvs\ia-workshop` (Python 3.12.3, `venv`) and verified pandas, numpy, scikit-learn, matplotlib and ipykernel were present.
  - With explicit human approval (Pedro), installed `seaborn 0.13.2` and `kagglehub 1.0.3` into that environment; the installation changed no repository files.
  - Registered the user-scope Jupyter kernelspec `Python (ia-workshop)` and resolved the issue where VSCode did not list it, by selecting `F:\venvs\ia-workshop\Scripts\python.exe` as the workspace interpreter.
  - Confirmed `kagglehub` is not needed at runtime because `data/Train.csv` is committed (the notebook only downloads when the file is missing); no Kaggle credentials were used.
  - Merged `origin/develop` into `feature/eda-pedro` (`1fd943f`) and renumbered the pending EDA entry from `A-002` to `A-006`, since `A-002` was already used by "Git integration branch workflow documentation"; the entry was appended after A-005.
  - Re-executed `01_eda_inicial.ipynb` from a clean kernel (execution counts 1-5, no error outputs) and committed the result as `871585e`; opened PR #46 into `develop`.
- **Files:** Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (A-006 entry, merged via PR #43), `01_eda_inicial.ipynb` (`871585e`, PR #46). Outside the repository: `F:\venvs\ia-workshop` (added `seaborn`, `kagglehub`).
- **Verification:** Import and version checks in `F:\venvs\ia-workshop`: pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, seaborn 0.13.2, kagglehub 1.0.3, ipykernel 7.4.0. Notebook execution counts 1-5 and no `output_type: error`; `git status` showed only `01_eda_inicial.ipynb`. PR #43 and PR #46 are merged into `develop`.
- **Outcome:** Environment prepared and reproducible for the session; A-006 and the notebook re-execution (`871585e`, PR #46) are merged into `develop`.
- **Pending tasks:** `requirements.txt` with pinned versions (assigned to Isbel); move split generation to `src/` per D-007.

---

<!-- Add new activities below using the same structure. Preserve previous records. -->

### A-012 — US-03: reproducible-environment deliverables (requirements, seed module, metrics convention)

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Pending human review
- **Objective:** Implement US-03 (issue #15) deliverables — `requirements.txt` with fixed versions, a central seed module (`src/config.py`), the `results/` metrics convention, and the versioned-CSVs decision points — without installing packages, committing, switching branches unsafely or touching other people's work.
- **Activities:**
  - Audited the working tree and branch topology before acting: 4 modified documentation files pending review, `stash@{0}` intact, HEAD `d13fc76` equal to `origin/feature/stratified-split` (PR #50), `origin/develop` at `f6bd6e0`.
  - Tested the branch switch to a develop-based working branch and git refused it (`AI_ACTIVITY_LOG.md` differs between HEAD and `develop` because of A-009 and also carries the pending A-010 changes); applied the non-destructive variant: created the branch ref `feature/environment-setup` at `origin/develop` without switching, leaving the deliverables as untracked files ready to commit on that branch later.
  - Re-audited seed usage restricted to project files (excluding the local ignored `.venv/`): `src/split_data.py` lines 12/50/56 (`RANDOM_STATE = 42`, PR #50) and `01_eda_inicial.ipynb` cells 8–9 (`random_state=42`); no other stochastic usage found.
  - Created `requirements.txt`: 7 runtime pins sourced from recorded runs (A-009 verification line; D-011 run with pandas 3.1.1 on Python 3.12.3) plus `pytest==9.2.0` as a dev pin marked as not yet exercised by a project run; scipy/joblib/threadpoolctl/cloudpickle/narwhals deliberately left as pip-resolved transitives (joblib becomes a direct dependency in US-12).
  - Created `src/config.py` with `RANDOM_STATE = 42` as the single source of truth, `src/__init__.py` so `src` is importable as a package, and `results/README.md` defining the one-CSV-per-model metrics convention with the required columns (timestamp, seed, model, partition) plus the D-010 columns (config, accuracy, macro_f1, per-class F1, notes).
  - Did not modify `.gitignore`: the versioned-CSVs decision stays with the team (D-013 remains Proposed).
- **Files:** Created: `requirements.txt`, `src/config.py`, `src/__init__.py`, `results/README.md`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m py_compile src/config.py src/__init__.py` exits 0; `python -c "from src.config import RANDOM_STATE"` prints 42; `python -m pip install --dry-run -r requirements.txt` resolves with no conflicts (would install cloudpickle 3.1.2, joblib 1.6.0, pandas 3.1.1, scikit-learn 1.9.1 and threadpoolctl 3.8.0; everything else already satisfied in the local environment); `git status` shows only the four new untracked files and the four pre-existing modified docs; `git diff --stat origin/develop -- data/` is empty; `src/split_data.py` unmodified; `stash@{0}` untouched. Note: the dry-run ran on the local Python 3.14.6 environment, not on the reference venv; final verification there is pending.
- **Outcome:** US-03 deliverables prepared as untracked additions, ready for review and commit on `feature/environment-setup` (created at `origin/develop`, `f6bd6e0`); no commits, installs or branch switches performed.
- **Pending tasks:** Human approval of the Python 3.12.3 pin and package versions, of the versioned-CSVs policy, and of the commit on `feature/environment-setup`; migrate `RANDOM_STATE` in `src/split_data.py` to `src.config` after PR #50 merges; README environment section; seed migration in `01_eda_inicial.ipynb` (US-05 context).
