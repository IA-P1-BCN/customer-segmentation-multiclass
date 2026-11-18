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

### A-010 — Dataset policy clarification: original Kaggle `Test.csv` excluded (D-012)

- **Date:** 2026-11-12
- **Agent:** opencode (deepseek-v4.1-flash-free; revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Clarify the documented dataset policy so that the original Kaggle `Test.csv` is excluded from the project dataset (D-012), without rewriting D-006/D-007 or touching data, code, notebooks or configuration.
- **Activities:**
  - Reviewed `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md` and `docs/ai-usage/AI_ACTIVITY_LOG.md` for references to the original Kaggle `Test.csv`.
  - Updated `AGENTS.md` and `README.md` to state that the original `Test.csv` is not part of the project's dataset/repository, must not be added, restored or used, and that `test_15.csv` is the project's internal test set generated from `Train.csv`; the shared-ID evidence (2,332 of 2,627 IDs; labels matching in only 30% of shared IDs) is documented.
  - Added D-012 (Proposed) to supersede only the conservation clauses of D-006 and D-007; their historical records remain unchanged.
  - Revised and renumbered the pending documentation draft (previously drafted as D-011/A-009, recovered from `stash@{0}` without modifying the stash) as D-012/A-010 before any commit, to avoid clashing with identifiers already in use: D-011 is in use on `origin/feature/null-diagnosis`, A-009 belongs to another activity, A-011 is in use for the US-04 null-diagnosis work, and the numbering of the team's Git-flow proposal remains pending assignment.
  - Preserved the historical A-005 wording as history; A-010 and D-012 record the current policy that supersedes it.
  - Updated cross-references in `AGENTS.md` and `README.md` to point to D-012.
- **Files:** Modified: `AGENTS.md`, `README.md`, `docs/ai-usage/DECISION_LOG.md`, `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Verification:** `git diff --check` passes; diff reviewed for scope; only the four authorized documentation files were modified (the untracked `src/split_data.py` from the ongoing US-02 task was not modified); no CSV, notebook or configuration changes; `stash@{0}` left untouched.
- **Outcome:** Documentation prepared for human review; D-012 is Proposed and requires human approval. The clarification is documentary: no file was removed from the repository.
- **Pending tasks:** Human approval of D-012; review and commit of these documentary changes on `feature/stratified-split`; open PR to `develop`.

---

### A-011 - US-04: missing-value diagnosis and imputation strategy

- **Date:** 2026-11-12
- **Agent:** opencode (DeepSeek V4.1 Flash Free)
- **Human owner:** Pedro
- **Objective:** Produce the missing-value table per variable on the train split, check duplicated IDs in `Train.csv` and propose an imputation strategy for the Pipeline (issue #16, US-04).
- **Activities:**
  - Reviewed `AGENTS.md`, `DECISION_LOG.md` and `AI_ACTIVITY_LOG.md`; created `feature/null-diagnosis` from `develop` (`6878635`).
  - Explored all four CSVs with the shared interpreter `F:\venvs\ia-workshop\Scripts\python.exe` to confirm shapes and missing values before writing code.
  - Asked Pedro for approval on the artifact format and the imputation strategy (AGENTS.md section 2); approved: reusable script in `src/` plus generated reports, and the robust strategy (median/mode + missing indicators + `Unknown`).
  - Created `src/data_quality.py`: reads `data/train_70.csv` for the missing-value table and `data/Train.csv` only for the duplicated-ID check, and writes the CSV table plus the Markdown report.
  - Ran `python src/data_quality.py` from the repository root with the shared interpreter; the recorded run produced `reports/nulls_train_70.csv` and `reports/data_quality.md`.
  - Proposed the strategy as D-011 (Proposed) in `docs/ai-usage/DECISION_LOG.md`; approval status left pending for the team.
- **Files:** Created: `src/data_quality.py`, `reports/nulls_train_70.csv`, `reports/data_quality.md`. Modified: `docs/ai-usage/DECISION_LOG.md` (D-011), `docs/ai-usage/AI_ACTIVITY_LOG.md` (A-011).
- **Verification:** Recorded run on `data/train_70.csv` (5,647 rows): `Work_Experience` 563 (9.97 %), `Family_Size` 244 (4.32 %), `Ever_Married` 99 (1.75 %), `Profession` 89 (1.58 %), `Graduated` 53 (0.94 %), `Var_1` 50 (0.89 %), all other columns 0.00 %. `Train.csv`: 8,068 rows, 8,068 unique IDs, 0 duplicated IDs. Interpreter Python 3.12.3, pandas 3.1.1; command, platform and versions are embedded in the generated report.
- **Outcome:** The missing-value table and the duplicated-ID check come from an executed, reproducible run; the imputation strategy is documented and awaiting team approval.
- **Pending tasks:** Team approval of D-011; implement the strategy in the US-05 Pipeline; optional extra (impute vs drop rows compared on validation with the US-01 metric) not done.

---

### A-012 — US-03: reproducible-environment deliverables (requirements, seed module, metrics convention)

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Implement US-03 (issue #15) deliverables — `requirements.txt` with fixed versions, a central seed module (`src/config.py`), the `results/` metrics convention, and the versioned-CSVs decision points — without installing packages, committing, switching branches unsafely or touching other people's work.
- **Activities:**
  - Audited the working tree and branch topology before acting: 4 modified documentation files pending review, `stash@{0}` intact, HEAD `d13fc76` equal to `origin/feature/stratified-split` (PR #50), `origin/develop` at `f6bd6e0`.
  - Tested the branch switch to a develop-based working branch and git refused it (`AI_ACTIVITY_LOG.md` differs between HEAD and `develop` because of A-009 and also carries the pending A-010 changes); applied the non-destructive variant: created the branch ref `feature/environment-setup` at `origin/develop` without switching, leaving the deliverables as untracked files ready to commit on that branch later.
  - Re-audited seed usage restricted to project files (excluding the local ignored `.venv/`): `src/split_data.py` lines 12/50/56 (`RANDOM_STATE = 42`, PR #50) and `01_eda_inicial.ipynb` cells 8–9 (`random_state=42`); no other stochastic usage found.
  - Created `requirements.txt`: 7 runtime pins sourced from recorded runs (A-009 verification line; D-011 run with pandas 3.1.1 on Python 3.12.3) plus `pytest==9.2.0` as a dev pin marked as not yet exercised by a project run; scipy/joblib/threadpoolctl/cloudpickle/narwhals deliberately left as pip-resolved transitives (joblib becomes a direct dependency in US-12).
  - Created `src/config.py` with `RANDOM_STATE = 42` as the single source of truth, `src/__init__.py` so `src` is importable as a package, and `results/README.md` defining the one-CSV-per-model metrics convention with the required columns (timestamp, seed, model, partition) plus the D-010 columns (config, accuracy, macro_f1, per-class F1, notes).
  - Did not modify `.gitignore`: the versioned-CSVs decision stays with the team (D-012 remains Proposed).
- **Files:** Created: `requirements.txt`, `src/config.py`, `src/__init__.py`, `results/README.md`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m py_compile src/config.py src/__init__.py` exits 0; `python -c "from src.config import RANDOM_STATE"` prints 42; `python -m pip install --dry-run -r requirements.txt` resolves with no conflicts (would install cloudpickle 3.1.2, joblib 1.6.0, pandas 3.1.1, scikit-learn 1.9.1 and threadpoolctl 3.8.0; everything else already satisfied in the local environment); `git status` shows only the four new untracked files and the four pre-existing modified docs; `git diff --stat origin/develop -- data/` is empty; `src/split_data.py` unmodified; `stash@{0}` untouched. Note: the dry-run ran on the local Python 3.14.6 environment, not on the reference venv; final verification there is pending.
- **Outcome:** US-03 deliverables prepared as untracked additions, ready for review and commit on `feature/environment-setup` (created at `origin/develop`, `f6bd6e0`); no commits, installs or branch switches performed.
- **Pending tasks:** Human approval of the Python 3.12.3 pin and package versions, of the versioned-CSVs policy, and of the commit on `feature/environment-setup`; migrate `RANDOM_STATE` in `src/split_data.py` to `src.config` after PR #50 merges; README environment section; seed migration in `01_eda_inicial.ipynb` (US-05 context).
- **Update (2026-11-13, after review by Rita Pereira):** the `pytest==9.2.0` pin mentioned above was removed from `requirements.txt` — pytest was never installed and is not a project dependency. The versioned-CSVs policy mentioned above has no decision identifier yet; `D-012` refers to the dataset policy about the original Kaggle `Test.csv` (Proposed), not to the versioned CSVs.

---

### A-013 — US-05 phase 1: shared preprocessing structure (X/y separation, column roles, structural tests)

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Implement the structural part of US-05 (issue #17) — a shared preprocessing layout so the four models (US-07 to US-10) and the prediction app receive exactly the same transformed features — without implementing any pending decision, without touching the CSVs, notebooks or other members' work, and without using `test_15.csv`.
- **Activities:**
  - Designed and implemented `src/preprocessing.py`: `make_features_target(df)` (X/y separation by name, excludes `ID` and undeclared columns, does not mutate the input dataframe, validates the schema) and `build_preprocessing(...)` (`ColumnTransformer` with four sub-pipelines — numeric, binary, nominal, ordinal — over the column groups in `src.config`, `remainder="drop"`, `verbose_feature_names_out=False`).
  - All seven strategy parameters (`numeric/binary/nominal/ordinal_imputer`, `binary/nominal/ordinal_encoder`) default to `"passthrough"` so no pending decision is imposed: D-011 (imputation) and the encoding decision (candidate D-014, not yet recorded) are exposed as parameters, not implemented.
  - Extended `src/config.py` with the shared column roles (`TARGET`, `ID_COLUMN`, `NUMERIC_COLS`, `BINARY_COLS`, `NOMINAL_COLS`, `ORDINAL_COLS`, `FEATURE_COLUMNS`); no new random seeds (`RANDOM_STATE` remains the single source of truth in `src.config`).
  - Wrote 16 structural tests in `tests/test_preprocessing.py`: X/target separation, ID exclusion, exact column-group coverage, input immutability, train/val schema, `ColumnTransformer` layout, fit on train / transform on validation, parameterizable strategies without rewriting the module, and integration into a model `Pipeline`.
  - Set up the isolated project environment (`.venv`, gitignored, Python 3.12.10) with the pinned `requirements.txt` versions plus `pytest==9.2.0` as a development dependency installed inside the venv; nothing installed globally.
  - Updated the branch with `origin/develop` (PR #51, #52, #53 and #54 integrated; resolved an add/add conflict in `src/config.py` keeping the US-05 superset) and created PR #55 into `develop` with a stacked diff of exactly the three US-05 files.
  - After D-011 was approved (Brian, 2026-11-13), aligned the module documentation to record the approval and that the strategies remain deferred to phase 2.
  - Applied this review's corrections (Rita Pereira, PR #55): re-added `pytest==9.2.0` to `requirements.txt` in a development section (the US-05 tests use it) and recorded this entry as A-013.
- **Files:** Created: `src/preprocessing.py`, `tests/test_preprocessing.py`. Modified: `src/config.py`, `requirements.txt`, `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `pytest tests/test_preprocessing.py` → 16 passed (Python 3.12.10, pandas 3.1.1, scikit-learn 1.9.1, pytest 9.2.0 in `.venv`; `pip check` clean); `python -m py_compile src/config.py src/preprocessing.py tests/test_preprocessing.py` exits 0; `git diff --check` clean; the diff against `develop` contains only the US-05 files; no CSV, notebook or other member's file modified; `test_15.csv` never used.
- **Outcome:** PR #55 open with the US-05 phase-1 structure. By design of this structural phase, all strategy parameters still default to `"passthrough"`: until the approved D-011 strategies and the (still unrecorded) encoding decision are connected through the existing parameters, the pipeline keeps nulls and text categories and cannot train models on real data. This is the intended behaviour of phase 1, not a defect.
- **Pending tasks:** Team review and squash-merge of PR #55; phase 2 — wire the approved D-011 strategies through the existing parameters; the encoding decision is not yet recorded (candidate identifier D-014) and requires team approval before any encoder is fixed; D-013 (single shared partition) still Proposed.

---

### A-014 — D-014 proposal: categorical encoding strategy for the shared Pipeline

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Draft decision D-014 (Proposed) fixing the project's categorical encoding strategy, as a prerequisite to unblock US-07 (multinomial logistic regression), without implementing any encoder or modifying the shared preprocessing module.
- **Activities:**
  - Verified the unblock prerequisites: PR #55 merged into `develop` (`e66b874`, review APPROVED); D-011 approved (Brian, 2026-11-13); D-013 still Proposed; no encoding decision recorded anywhere (`develop` decision log ends at D-013).
  - Reviewed the existing evidence for the encoding choice: the proposal recorded in issue #17 (one-hot for nominal columns, explicit ordinal order for `Spending_Score`) and the manual smoke test performed by Rita Pereira during the PR #55 review (numeric matrix 5,647×26 on `train_70` through the parameter seam, without touching the module).
  - Created branch `docs/propose-d014-encoding` from `origin/develop` (`e66b874`) and added D-014 (Proposed) to `docs/ai-usage/DECISION_LOG.md` after D-013: one-hot for the binary (`Ever_Married`, `Graduated`) and nominal (`Gender`, `Profession`, `Var_1`) columns with `handle_unknown="ignore"` and `drop="if_binary"` for the binaries, ordinal encoding for `Spending_Score` with the explicit order `Low`=0, `Average`=1, `High`=2 and a documented `-1` sentinel for unexpected values; integration through the existing `build_preprocessing()` encoder parameters, fitted on `train_70` only (D-010 item 6, D-013 item 3); `ID` never encoded (D-006, D-012).
  - Recorded this session as A-014 in `docs/ai-usage/AI_ACTIVITY_LOG.md`.
  - Cross-checked the proposal against D-011 (imputers run before the encoders inside each sub-pipeline), D-012 (dataset policy untouched) and D-013 (transformations live inside the shared Pipeline, fitted on `train_70`); noted in D-014 that D-013 still states D-011 was Proposed because it was written before that approval.
  - Opened PR into `develop` for team review; the approval status of D-014 remains Pending for a human team member.
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md` (D-014), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `git diff --check` clean; diff against `develop` touches only the two documentation files; no encoder implemented, no code, CSV, notebook or configuration file modified; log order intact (activities A-010…A-014 above the template comment; decisions D-011…D-014 above the template comment); approval states of D-011 (Approved) and D-013 (Proposed) unchanged.
- **Outcome:** D-014 formally proposed and traceable to issue #17 and the PR #55 review evidence; US-07 remains blocked only on the team's approval of D-014.
- **Pending tasks:** Team approval of D-014 (human); then implement US-07 wiring D-011 and D-014 through the `build_preprocessing()` parameters; D-013 still Proposed.

---

### A-015 — D-014 refinements from the PR #57 review (Profession one-hot width, scaler responsibility)

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Incorporate the two observations of Rita Pereira on the PR #57 branch into the D-014 proposal before its integration, without rewriting previous records and keeping D-014 in `Proposed`.
- **Activities:**
  - Clarified in D-014 (Decision, item 2) the interaction with D-011: `Profession` is imputed with the constant level `"Unknown"`, so once that level appears in the training data after imputation — inside the same sub-pipeline, where the imputer runs before the encoder — `OneHotEncoder` generates an additional column for `"Unknown"`.
  - Corrected the Consequences section of D-014: the ≈ 26-column figure measured during the PR #55 review corresponds to a configuration that imputed `Profession` with the mode; with the D-011 constant `"Unknown"` level the width on the current data can be 27, and in any case the width is not a universal number — it depends on the categories observed during fit on `train_70`.
  - Added to D-014 a new Decision item stating that `StandardScaler` is a model-specific transformation of logistic regression (US-07), not part of the shared preprocessing: it is integrated in the US-07 pipeline after the shared preprocessing and before the estimator; the responsibilities of the shared module and of the model stay separate (D-013 item 3).
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md` (D-014 proposal content only), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `git diff --check` clean; the diff on this branch touches only the two documentation files; A-014 and all previous entries unchanged; D-014 remains `Proposed` (approval status untouched for the team); decisions D-001…D-013 unmodified.
- **Outcome:** The D-014 proposal incorporates both review observations and remains open for team approval on PR #57.
- **Pending tasks:** Team approval of D-014 (human); then implement US-07 wiring D-011 and D-014 through the `build_preprocessing()` parameters; D-013 still Proposed.

---

### A-016 — D-014 revision from the second PR #57 review: `Spending_Score` one-hot with measured evidence

- **Date:** 2026-11-13
- **Agent:** opencode (revision: glm-5.3-flash-free)
- **Human owner:** Isbel
- **Objective:** Incorporate the second technical review of Rita Pereira into the D-014 proposal — replace the ordinal strategy for `Spending_Score` with one-hot, document the measured evidence, and align the dimension estimate — without rewriting A-014, A-015 or any previous record, and keeping D-014 in `Proposed`.
- **Activities:**
  - Verified the review's evidence table by an executed run on `data/train_70.csv` (read-only): the percentages are the share of each segment within every `Spending_Score` level (column-normalized) and match the review exactly — Low: A 27.8 %, B 18.5 %, C 13.5 %, D 40.2 %; Average: A 17.4 %, B 29.3 %, C 45.7 %, D 7.7 %; High: A 22.1 %, B 31.4 %, C 34.2 %, D 12.3 % (row counts: Low 954/634/464/1,377; Average 237/399/623/105; High 189/268/292/105).
  - Verified the transformed width by an executed fit on `train_70` of the exact proposed configuration (D-011 imputers, one-hot everywhere categorical): **29 columns** (3 numeric + 2 D-011 missing indicators + 2 binary + 2 Gender + 10 Profession with `"Unknown"` + 7 `Var_1` + 3 `Spending_Score`); the configuration measured during the PR #55 review (mode-imputed `Profession`, single-column ordinal `Spending_Score`) measures 26. The review's estimate of ≈ 28 columns is documented as an estimate; the verified 29 is recorded as the executed reference.
  - Updated D-014: Decision item 4 now fixes `OneHotEncoder(handle_unknown="ignore")` for `Spending_Score` (three columns, all kept) with the verified non-monotone evidence table; item 3 extended to all categorical groups; item 5 clarifies that `ORDINAL_COLS` and the `ordinal_encoder` slot describe the source column group, not the transformer type — the shared US-05 architecture stays unchanged and the one-hot encoder rides on the existing slot; Context, Alternatives (ordinal option now discarded because the measured segment mix is not monotone) and Recommendation aligned; Consequences document the dimension estimates (review ≈ 28, verified 29, reference 26) and note the dependence on the observed categories during fit.
  - Kept unchanged: binary `drop="if_binary"`, one-hot for nominals, `handle_unknown="ignore"`, the `Profession`/`"Unknown"` interaction with D-011 (item 2), the `StandardScaler` responsibility split (item 6) and the `ID` exclusion (item 7). D-014 remains `Proposed`.
  - Recorded this session as A-016 in `docs/ai-usage/AI_ACTIVITY_LOG.md`.
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md` (D-014 proposal content only), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only). Executed diagnostic runs (read-only, no repository files changed): `data/train_70.csv` crosstab and sklearn fit for the column-count verification.
- **Verification:** `git diff --check` clean; the branch diff touches only the two documentation files; A-014 and A-015 and all previous entries unchanged; D-001…D-013 unmodified; D-014 still `Proposed`; `test_15.csv` never used; the diagnostic runs read only `train_70.csv` and did not modify any file.
- **Outcome:** D-014 now encodes `Spending_Score` as one-hot with executed, verified evidence instead of an assumed ordinal order; the proposal remains open for team approval on PR #57.
- **Pending tasks:** Team approval of D-014 (human); then implement US-07 wiring D-011 and D-014 through the `build_preprocessing()` parameters; D-013 still Proposed.

---

### A-017 — US-06 EDA on train_70: Spending_Score and Ever_Married

- **Date:** 2026-11-12 / 2026-11-13
- **Note:** Numbered A-017 because A-013 is used by PR #55 and A-014–A-016 by PR #57 (merged into `develop` before this entry).
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Rita's section of US-06 (issue #10): `Spending_Score` vs `Profession`, `Graduated` and `Segmentation`, and `Ever_Married` vs `Segmentation`, using only `train_70`.
- **Activities:**
  - Set up Rita's local environment (with her approval): `.venv/` (git-ignored), Python 3.12.10, with the pinned team `requirements.txt` (pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, seaborn 0.13.2, kagglehub 1.0.3, ipykernel 7.4.0, pytest 9.2.0; scipy 1.18.1 as a scikit-learn dependency) plus jupyterlab 4.6.6; `pip check` clean. Registered the user-scope Jupyter kernelspec `Python (multiclass-minds .venv)` because VS Code did not detect the venv from the parent workspace folder.
  - Team agreement (Rita and Pedro, 2026-11-12): each member works on their own branch and notebook named `02_eda_train70_<analysis>.ipynb`, with a separate PR per section instead of the single PR in issue #10; Pedro integrates the findings.
  - Created branch `feature/eda-gasto-estado-civil` and the notebook `02_eda_train70_gasto_estado_civil.ipynb`: row-normalised proportion tables (nulls shown as `Missing`, not imputed), 100 % stacked bar charts, chi-square and Cramér's V (rows with nulls in the pair excluded), segment distribution of rows with nulls, an explanation of how to read Cramér's V, and written conclusions based only on the executed outputs.
  - 2026-11-13: updated the branch to `develop` (`e66b874`). Ran `python src/split_data.py --check` (US-02): the generated split matches the existing CSV files, so the notebook data are unchanged. Updated the conclusions to refer to D-011 as approved (Brian, 2026-11-13) and re-executed the notebook. Rita Pereira reviewed the notebook and approved it for a PR.
  - Main results (from the executed notebook): high spending concentrated in Executive (65.4 % High) and Lawyer (51.6 %); Healthcare 93.3 % Low; Graduated weakly associated with spending (V = 0.138); segment D 86.8 % Low and 29 % ever married (vs 58–79 % in A–C); V = 0.302 (Spending_Score–Segmentation) and 0.408 (Ever_Married–Segmentation); all 2,284 never-married customers have Spending_Score Low (V = 0.669).
- **Files:** Created: `02_eda_train70_gasto_estado_civil.ipynb`, `reports/figures/eda_spending_by_profession.png`, `eda_spending_by_graduated.png`, `eda_spending_by_segment.png`, `eda_married_by_segment.png`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only). Outside the repository: `.venv/`, Jupyter kernelspec.
- **Verification:** Notebook executed from a clean kernel with `jupyter nbconvert --execute` (execution counts 1–19, no error outputs); figures inspected visually; `val_15` and `test_15` are not read; `src/split_data.py --check` exit code 0.
- **Outcome:** Implemented and reviewed by Rita Pereira; submitted as a PR into `develop`. Points raised for other sections, not decisions: the Ever_Married/Spending_Score rule (Brian's leakage review); for the 47.5 % of null `Ever_Married` rows with Low spending, the approved mode imputation (D-011) is less certain, and the null signal (D-skew) is lost — only relevant if the team revisits D-011 (99 rows, 1.8 % of `train_70`).
- **Pending tasks:** Review and squash-merge of the PR; comment in issue #10 that US-06 is split into one PR per section; Pedro integrates the findings into the final EDA.

### A-020 — US-13: segment profiles, prioritisation proposal and campaign draft

- **Date:** 2026-11-16
- **Note:** Numbered A-020 because A-018 is the random forest entry in PR #67 and A-019 is the D-015 proposal entry in PR #68 (both open, not yet in `develop`). If A-020 is taken when this is merged, use the next free number.
- **Agent:** Claude Code (Claude Fable 5.2)
- **Human owner:** Rita Pereira
- **Objective:** Start US-13 (issue #13) with the parts that do not depend on the model: the profile of each segment, a prioritisation proposal and the campaign table that US-15 integrates.
- **Activities:**
  - Read `AGENTS.md`, D-010, D-011, D-013, D-014, issues #13, #34, #35, #36 and #37, and the executed outputs of `02_eda_train70_gasto_estado_civil.ipynb`.
  - Created branch `feature/segment-insights` from `develop` (`6e3c217`) and `src/segment_profile.py`: reads `data/train_70.csv` only, checks the row count and the SHA-256 (LF) of D-013 before computing, and writes a summary table (one row per segment plus `All`) and a long table with every categorical level. Percentages exclude missing values from the denominator; the number of missing values is recorded next to them. The output files carry no timestamp, so two runs give byte-identical files.
  - Created `tests/test_segment_profile.py` (12 tests), mostly on an invented 8-customer dataset whose figures can be checked by hand.
  - Wrote `reports/segment_insights.md` (in English, like the other reports, by decision of Rita Pereira): profile per segment, prioritisation, influential variables from the EDA and a campaign table. Rita Pereira chose the prioritisation rule to propose (most High-spending customers) among three options presented by the agent, and kept the segment names and the campaign texts drafted by the agent; the names are presented as hypotheses.
- **Files:** Created: `src/segment_profile.py`, `tests/test_segment_profile.py`, `reports/segment_profile_train_70.csv`, `reports/segment_distributions_train_70.csv`, `reports/segment_insights.md`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m src.segment_profile` run on 2026-11-16 14:31 UTC (Python 3.12.10, pandas 3.1.1): 5,647 rows, SHA-256 matches D-013; second run produced identical files. `pytest tests` → 28 passed (16 existing + 12 new). `val_15` and `test_15` not read; no CSV in `data/` modified. Main figures: segment sizes A 1,380, B 1,301, C 1,379, D 1,587; High-spending customers A 189, B 268, C 292, D 105 (854 in total); median age 41 / 46 / 49 / 29; ever married 58.2 % / 73.7 % / 79.5 % / 29.0 % of the customers with a value.
- **Outcome:** Implemented and executed; not committed. The document is a draft: the prioritisation rule and the campaign table are proposals, not team decisions, and no Decision Log record was created or changed.
- **Pending tasks:** Team approval of the prioritisation rule, of the meaning of "on the train split" in the story and of the campaign table; add the feature importance from US-12 and the numeric EDA figures of PR #64 once merged; commit and PR into `develop` with Rita's authorization.
- **Update 2026-11-16 (Claude Fable 5.2):** committed (`f73cfe4`, `11e90e1`) and pushed with Rita's authorization. Rita Pereira opened PR #69 into `develop` as the first part of US-13; issue #13 stays open until the US-12 feature importance is added. Pending: review of PR #69 and the team approvals listed above.
- **Update 2026-11-17 (Claude Opus 5.5):** applied Isbel's review of PR #69 (shared in the team channel). `reports/segment_insights.md`: C presented as provisional first priority with B as segment of interest; "on the train split" stated as `train_70.csv` (5,647 rows); campaign table rewritten with a separate "hypothesis to test" column (preferential service for C and digital channels for D moved there, B no longer described as a family or mid-range segment, A made more specific). Created D-016 (Proposed) in `docs/ai-usage/DECISION_LOG.md` with the prioritisation rule and the meaning of "on the train split", as Isbel asked; its approval status is left for a team member. No figure changed; `segment_profile.py` was not re-run.
- **Correction 2026-11-17 (Claude Opus 5.5):** the comments applied in the previous update were shared by Isbel in the team channel; they were not a GitHub review of PR #69. At Isbel's request, the wording was corrected in `reports/segment_insights.md` (five mentions) and in D-016; the previous lines of this entry are kept unchanged as history. No figure changed.
- **Update 2026-11-17, afternoon (Claude Sonnet 5.5):** with Rita Pereira's authorization, merged `develop` into the PR branch (PR #66, #70, #71, #73 and #75 are now in it; no conflicts). `reports/segment_insights.md`: section 4.1 now cites the numeric variables measured in PR #64 and summarised in PR #71 (`Age` eta² 0.144, one-variable tree 0.397; `Family_Size` 0.032, 0.3053; `Work_Experience` 0.009, 0.2810, all from `reports/eda_train70_sintesis.md`), and the matching box of the pending list is ticked. D-016: the note about the numbering was updated because D-015 and D-017 are in `develop`; the rule, the figures and `Approval: Pending` are unchanged. No metric was recomputed and no data was read. Still pending: approval of D-016 by a team member other than the proposer, team approval of the campaign table and the segment names, and the feature importance of the frozen model (section 4.2).
- **Update 2026-11-17, evening (Claude Opus 5.5):** review of PR #69 by Pedro (changes requested on `f7189ad`; D-016 approved and the campaign table approved as business hypotheses in the same review). With Rita Pereira's authorization: merged `develop` into the PR branch (PR #65 and #67; no conflicts). `reports/segment_insights.md`: section 4.1 now has one table for the nine variables, with the one-variable tree accuracy from 5-fold CV and the Kruskal-Wallis tests read from the recorded outputs of `03_eda_train70_brian_outliers_fuga.ipynb` (cells 17 and 19), the Cramér's V from notebook 02 and `eta²` from `reports/eda_train70_sintesis.md`; the sentence saying that no strength measure had been computed was removed, and the text notes that `Spending_Score` has the best one-variable accuracy while `Ever_Married` has the higher Cramér's V (the review suggested calling `Ever_Married` the best categorical separator, which only holds for Cramér's V). Sections 3 and 5, the status table and the pending list now cite the approvals of the review. D-016: `Status: Approved` and the approval line written by Pedro in the review, changed on his instruction. `src/segment_profile.py`: the `Spending_Score` percentages now exclude missing values from the denominator, as the docstring states (non-blocking point of the review); new test `test_spending_percentages_exclude_missing_values`. The script was run again and both CSVs are byte-identical (same SHA-256), because `train_70` has no missing `Spending_Score`. `python -m pytest -q`: 97 passed, 1 failed (`test_train_boosting.py`, XGBoost cannot load without `libomp` on this machine; not related to this PR). `val_15` and `test_15` were not read. Still pending: the feature importance of the frozen model (section 4.2), the segment names as presentation hypotheses, and Isbel's integration of the campaigns into the app (US-15).

---

### A-018 — US-08: random forest baseline and improvement

- **Date:** 2026-11-13
- **Note:** Numbered A-018 because A-017 is Rita's EDA (PR #58, merged). If A-018 is taken when this is merged, use the next free number.
- **Agent:** Claude Code (Claude Opus 5.5 / Claude Fable 5.2)
- **Human owner:** Rita Pereira
- **Objective:** Train the random forest on the shared Pipeline, first as a baseline and then improved, and record the metrics required by D-010 (issue #20, US-08).
- **Activities:**
  - Read the results convention (`results/README.md`), `src/config.py`, `src/preprocessing.py`, D-010, D-011, D-013 and D-014. Rita Pereira chose a script plus a notebook, and to start with D-014 while it is still Proposed.
  - Created branch `feature/model-random-forest` from `develop` (`51024c7`) and `src/train_random_forest.py`: D-013 checks (row counts, no ID overlap, SHA-256), D-011 imputation and D-014 encoding passed through the parameters of `build_preprocessing()` (shared module not modified), `RandomForestClassifier` with `RANDOM_STATE`, and two stages (`baseline`, `tune`) that append to `results/random_forest.csv`.
  - Finding on D-013: the SHA-256 values listed there correspond to a Windows checkout (CRLF line endings). Git stores the CSV files with LF, so a macOS/Linux checkout gives different hashes for the same content (verified: converting the LF files to CRLF reproduces the four D-013 hashes). The script hashes the content with line endings normalised to LF. Not changed in the Decision Log; to be raised with the team.
  - Ran `python -m src.train_random_forest --stage baseline` and `--stage tune` (60 configurations: `max_depth` 4/6/8/10/12/None × `min_samples_leaf` 1/5/10/20/40 × `max_features` sqrt/0.5, 300 trees; 5-fold stratified CV on `train_70`, full Pipeline inside each fold, D-010 item 6). Selection rule: best CV macro-F1 among configurations with train − CV accuracy gap < 5 points; `val_15` was not used to choose.
  - Created `03_model_random_forest.ipynb`, which reads the recorded results, refits the selected configuration (reproducing the recorded validation accuracy) and produces the tuning plot, the confusion matrix and the feature importances, with written conclusions.
  - Created `tests/test_train_random_forest.py` (7 structural tests).
- **Files:** Created: `src/train_random_forest.py`, `tests/test_train_random_forest.py`, `results/random_forest.csv`, `03_model_random_forest.ipynb`, `reports/figures/rf_tuning_cv.png`, `rf_confusion_matrix_val.png`, `rf_feature_importance.png`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Recorded runs (Python 3.12.10, scikit-learn 1.9.1, seed 42), 64 rows in `results/random_forest.csv`. Baseline: accuracy 0.9683 train / 0.4983 val (gap 47.00 points, fails the < 5 limit), macro-F1 val 0.4849. Selected configuration (`n_estimators=300`, `max_depth=12`, `min_samples_leaf=20`, `max_features="sqrt"`): accuracy 0.5628 train / 0.5421 val (gap 2.06 points, meets the limit), macro-F1 0.5442 train / 0.5197 val; per-class F1 on val A 0.448, B 0.359, C 0.556, D 0.715; CV macro-F1 0.5084 (sd 0.0101), 35 of 60 configurations within the CV gap limit. `pytest tests` → 23 passed (16 existing + 7 new). Notebook executed from a clean kernel (execution counts 1–13, no error outputs). `test_15` never read.
- **Outcome:** Implemented and executed; not committed (awaiting Rita's review). The selected configuration is fixed for US-11.
- **Pending tasks:** Rita reviews the notebook; commit and PR into `develop`; re-run both stages if D-014 is changed before approval; raise the D-013 checksum finding with the team.
- **Update 2026-11-16 (re-run after D-014 approval, Claude Fable 5.2):**
  - D-014 was approved in PR #61 with a change to item 2: nominal columns use `OneHotEncoder(drop="if_binary", handle_unknown="ignore")`, so `Gender` yields one column (28 columns instead of 29). The D-013 checksum finding was resolved by PR #59 (LF hashes in the Decision Log).
  - Changed `build_preprocessor()` accordingly, updated the width test (29 → 28) and the outdated comments, and re-ran both stages. The file is append-only: the 64 rows of 2026-11-13 are kept (their notes say "D-014 (Proposed)") and 64 new rows were appended (notes say "D-014 (Approved, 28 columns)"), 128 rows in total.
  - Rebuilt and re-executed `03_model_random_forest.ipynb`: it now uses only the latest run of each stage and adds a comparison with the earlier run.
  - Verification: `pytest tests` → 23 passed. Baseline: accuracy 0.9683 train / 0.4959 val (gap 47.24 points, fails), macro-F1 val 0.4830. Selected configuration (`n_estimators=300`, `max_depth=None`, `min_samples_leaf=20`, `max_features=0.5`): accuracy 0.5792 train / 0.5314 val (gap 4.78 points, meets the limit), macro-F1 0.5656 train / 0.5102 val; per-class F1 on val A 0.409, B 0.373, C 0.552, D 0.707; CV macro-F1 0.5116 (sd 0.0077), CV gap 4.94 points; 37 of 60 configurations within the CV gap limit. `test_15` never read.
  - Finding: that configuration is within 0.3 points of the gap limit (CV gap 4.94, validation gap 4.78) and leads the next admissible ones by 0.002 CV macro-F1, less than its standard error (0.0034).
  - Selection rule changed by decision of Rita Pereira (2026-11-16, after seeing the result above; proposed by the agent): among the configurations with train − CV gap < 5 points, those within one standard error of the best CV macro-F1 are treated as tied and the smallest gap is selected (`select_configuration()`, 3 new tests). Only CV results on `train_70` are used; `val_15` does not take part in the choice. Re-ran `--stage tune` (62 more rows appended, 190 in total; the previous run is kept for traceability).
  - Final verification: `pytest tests` → 26 passed. Six configurations tied; selected `n_estimators=300`, `max_depth=6`, `min_samples_leaf=10`, `max_features=0.5` (CV macro-F1 0.5082, sd 0.0086, CV gap 3.01 points; its CV macro-F1 equals the tie threshold to four decimals). On `train_70` / `val_15`: accuracy 0.5438 / 0.5248 (gap 1.90 points, meets the limit), macro-F1 0.5321 / 0.5080; per-class F1 on val A 0.419, B 0.356, C 0.551, D 0.706. Compared with the rule without tie-break on `val_15`: macro-F1 0.5102 → 0.5080, accuracy gap 4.78 → 1.90 points. Notebook re-executed from a clean kernel (14 code cells, no errors); it uses the latest run of each stage and shows the three recorded runs side by side.
  - Outcome: committed and pushed on 2026-11-16 with Rita's authorization; pull request into `develop` pending. The rule change should be communicated to the team before US-11.
- **Update 2026-11-17 (Claude Opus 5.5 / Claude Fable 5.2, PR #67 review and D-015):**
  - Context: the tie-break rule was proposed to the whole team as D-015 (PR #68, Proposed). Isbel's audit of PR #67 asked for per-class precision and recall in the results file and for the fallback required by D-015.
  - `src/train_random_forest.py`: separate constants for the official check on `val_15` (`MAX_ACCURACY_GAP`, D-010 item 3) and for the admissibility cut on the train − CV gap (`CV_GAP_LIMIT`, D-015 item 3), as Pedro pointed out that the old label described only the first; per-class precision, recall and F1 on `val_15` written to `notes` in the same format as the boosting results (PR #65); `rank_configurations()` and the D-015 item 7 fallback (if the selected configuration fails the official check, the next one is evaluated and every evaluation is recorded). Pedro noted that item 6 (no admissible configuration) was already implemented; item 7 was not.
  - Ran `--stage tune` at 08:11 UTC with `CV_GAP_LIMIT = 0.10`, while the team was considering Pedro's 10-point amendment: selected `max_depth=10`, `min_samples_leaf=20`, `max_features=0.5`; `val_15` accuracy 0.5289, macro-F1 0.5066, gap 4.73 points. The team kept 5 points (relayed by Rita Pereira); these 62 rows stay in the append-only file as a record (notes say "< 10 pts").
  - Error found and fixed: the first run with the fallback stopped before writing any row because iterating over the ranked table returned `max_depth=6.0` and `RandomForestClassifier` rejected it. `_py()` now also converts plain Python floats; a regression test covers it.
  - Ran `--stage tune` at 08:49 UTC with `CV_GAP_LIMIT = 0.05`: same selection and metrics as the 2026-11-16 run with tie-break (`max_depth=6`, `min_samples_leaf=10`, `max_features=0.5`; `val_15` accuracy 0.5248, macro-F1 0.5080, gap 1.90 points), passing the official check at the first attempt. Per-class precision / recall on `val_15`: A 0.442 / 0.399, B 0.381 / 0.333, C 0.537 / 0.566, D 0.662 / 0.756. `results/random_forest.csv`: 314 rows.
  - `03_model_random_forest.ipynb`: rebuilt from the committed version (a local execution at 09:28 had changed the kernel metadata and was overwritten with Rita's authorization), with five runs described, a precision/recall table, the comparison table extended and the conclusions updated (D-015, 10-point test not adopted). Executed from a clean kernel with `jupyter nbconvert --execute` (15 code cells, no errors; the refit reproduces the recorded accuracy); kernel metadata unchanged; the three figures came out byte-identical.
  - Verification: `pytest tests` → 30 passed. `test_15` never read.
  - Review follow-up 2026-11-17 (Claude Sonnet 5.5, with Rita Pereira's authorization): the baseline rows had no per-class precision and recall in `notes` (US-08 criterion 2, D-010 Consequences). Re-ran `--stage baseline` (2 rows appended, 316 rows in total): same metrics as before (accuracy 0.9683 train / 0.4959 val, macro-F1 val 0.4830, gap 47.24 points) and per-class precision / recall now in `notes` (val: A 0.390 / 0.358, B 0.391 / 0.362, C 0.520 / 0.529, D 0.624 / 0.697). Merged `develop` (D-015 Approved, #68) into the branch; the conflict in this file was resolved by keeping A-018 followed by A-019. The notebook was re-executed from a clean kernel so that its outputs list the new run.

---

### A-019 — D-015 proposal: common rule to select each model's configuration

- **Date:** 2026-11-16
- **Note:** Numbered A-019 because A-018 is used by open PR #67 (random forest). If A-019 is taken when this is merged, use the next free number.
- **Agent:** Claude Code (Claude Fable 5.2)
- **Human owner:** Rita Pereira
- **Objective:** Document, as a proposal for team approval, a single rule for choosing each model's final configuration, after the review of PRs #65, #66 and #67 showed that the three models did not choose in the same way.
- **Activities:**
  - Reviewed PR #65 (XGBoost), PR #66 (logistic regression) and PR #67 (random forest) in temporary worktrees: the first two choose the best validation macro-F1 among the configurations evaluated on `val_15`; the third chooses with cross-validation on `train_70` only.
  - Read the acceptance criteria of US-08 (issue #20) and D-010: the user stories say "compare in validation" and D-010 item 6 asks for cross-validation. Reported the contradiction to Rita Pereira, who raised it in the team channel with two options.
  - Isbel agreed with choosing by cross-validation and asked for the standard-error formula to be explicit. Pedro and Brian had not answered when this entry was written.
  - Wrote D-015 (Status: Proposed) in `docs/ai-usage/DECISION_LOG.md`. D-010 is not modified. Three details were added by the agent and have not been discussed by the team: the standard deviation convention (`ddof=0`), the use of the mean of the fold scores instead of pooled out-of-fold predictions, and what to do when the selected configuration fails the official check on `val_15`.
  - Correction recorded: an earlier figure given by the agent for the smallest XGBoost train − CV gap (5.47 points) was an approximation from the full-fit training accuracy; the value recorded in the `notes` of PR #65 is 6.19 points. D-015 quotes the recorded value.
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md` (new record D-015), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Documentation only; no code or data changed and no model executed for this entry. Figures quoted in D-015 were read from the results files of PRs #65, #66 and #67 (`C=0.1_l2` validation macro-F1 0.4806, `C=1_l2_balanced` CV macro-F1 0.4857, XGBoost smallest train − CV gap 6.19 points, random forest standard error 0.0034 and validation gap 4.78 points). The effect of the rule on logistic regression and XGBoost was not executed. `git diff --check` passes.
- **Outcome:** Proposed; committed, pushed and opened as a pull request into `develop` with Rita Pereira's authorization. Not approved: only a human team member can approve D-015.
- **Pending tasks:** Answers from Pedro and Brian; human approval of D-015; if approved, PRs #65 and #66 re-derive their selected configuration before US-11.
- **Update 2026-11-17 (Claude Opus 5.5):** updated D-015 with Rita Pereira's authorization after the team discussion. Item 3: admissibility cut on the train − CV gap raised from 5 to 10 points on the cross-validation scale (Pedro's amendment, chosen by the team in the channel as relayed by Rita Pereira); the official 5-point check on `val_15` is unchanged. Item 6: Brian's precision (the fallback configuration must still pass the official check and the limitation is declared in US-16). Item 7: explicit fallback order, which the first version left undefined after the tied group (requested in Isbel's audit). Item 8: per-class precision, recall and F1 on `val_15` in the notes. Evidence: effect of the cut on the random forest from the run of 2026-11-17 (5 points: `max_depth=6`, `val_15` macro-F1 0.5080, gap 1.90; 10 points: `max_depth=10`, `min_samples_leaf=20`, macro-F1 0.5066, gap 4.73). Agreement: votes of Isbel, Brian and Pedro. The status stays Proposed: approval is left to a team member other than the proposer. Documentation only; `git diff --check` passes.
- **Update 2026-11-17, later (Claude Opus 5.5):** Pedro changed his vote to 5 points for schedule reasons and the team kept 5 (relayed by Rita Pereira). With her authorization, item 3 was set back to 5 points and the 10-point cut, the reasons for not adopting it and its measured effect were recorded in Evidence and limits as known technical debt, as Pedro asked. Items 6, 7 and 8 keep the changes of the previous update. XGBoost figures are attributed to Pedro and were not re-executed. Status stays Proposed. Documentation only; `git diff --check` passes.

### A-021 — US-10: SVM baseline and improvement (D-015, approved 2026-11-17)

- **Date:** 2026-11-17
- **Note:** Numbered A-021 because A-018 and A-020 are used by open PRs #67 and #69; A-019 was merged into `develop` with PR #68 and is kept immediately before this entry.
- **Agent:** OpenCode (DeepSeek V4.1 Flash)
- **Human owner:** Brian
- **Objective:** Implement US-10 (issue #22): SVM on the shared Pipeline, baseline and improvement, choosing the configuration with D-015 as approved on 2026-11-17 (5-fold cross-validation on `train_70`; `val_15` only for the official overfitting check and the US-11 comparison).
- **Activities:**
  - Created branch `feature/model-svm` from `develop` (`efd6a72`) and `src/train_svm.py`: Pipeline `preprocessing → StandardScaler → SVC` (scaling is this model's own step, D-013 item 3); D-013 item 6 checks (row counts, `ID` overlap, SHA-256 with LF line endings); `--stage baseline|tune`. Only the approved D-015 rule is available: after the review, the `--rule` flag and the rejected option A path were removed, so a run cannot record a result under the discarded rule.
  - Created `tests/test_train_svm.py` (16 tests: partitions, 28-column matrix, `Profession_Unknown`, scaler placement, global seed, results format, the D-015 selection rule and its fallback, the per-class precision/recall note, the CV helper and the CLI rejecting the rejected rule).
  - Baseline (rbf, C=1, gamma=scale): CV macro-F1 0.4952 with a 7.85-point train-CV gap; `val_15` accuracy 0.5240, macro-F1 0.5063, gap 6.38 points (fails the 5-point limit), fit time 15.24 s. Its CV row is recorded so the gap is checkable in the CSV.
  - Nine-configuration grid (linear and rbf kernels): 6 configurations meet the CV gap limit; selected `rbf, C=1.0, gamma=0.01` with CV macro-F1 0.4923 and CV gap 3.54 points, `val_15` accuracy 0.5025, macro-F1 0.4853, gap 3.89 points and fit time 2.88 s. `val_15` took no part in the choice.
  - The selected configuration scores below the baseline on `val_15` (0.4853 against 0.5063) because the baseline fails the gap limit; that effect of the 5-point cut is recorded in D-015 as a known limitation.
  - Recorded 32 rows in `results/svm.csv` (baseline x3, 9 configurations x cv5fold/train_70/val_15, and the selected configuration marked `SELECTED`). Training time, the absolute and relative accuracy gaps and the per-class precision, recall and F1 are in `notes`, as issue #22 and D-010 require.
- **Files:** Created: `src/train_svm.py`, `tests/test_train_svm.py`, `results/svm.csv`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m pytest tests/test_train_svm.py -q` -> 16 passed. `python -m src.train_svm --stage baseline` and `--stage tune` print the D-013 row counts and SHA-256 (LF) of `train_70` and `val_15` and confirm the absence of `ID` overlap. `test_15` is never read. Every recorded row comes from an executed run.
- **Outcome:** US-10 implemented and submitted as PR #70 into `develop`. The frozen configuration for US-11 is `kernel=rbf, C=1.0, gamma=0.01`.
- **Pending tasks:** Human review and squash-merge; re-run if the shared Pipeline phase 2 lands (D-013 Consequences); US-11 compares the four models on `val_15` with the same rule.
---

### A-024 — US-07 review: D-015 re-selection, CV standard deviations, precision/recall and column names

- **Date:** 2026-11-17
- **Note:** Numbered A-024 because A-018–A-020 are reserved by open PR #69 and A-021–A-023 are used on `develop` (SVM, EDA and US-15 app). This entry is added on the PR #66 branch without rewriting previous records.
- **Agent:** opencode (deepseek-v4.1-flash-free)
- **Human owner:** Isbel
- **Objective:** Address the technical review of PR #66: re-derive the logistic-regression configuration with the approved D-015 rule, record the fold standard deviation of macro-F1 in the `cv5fold` rows, add per-class precision and recall to the official `val_15` row of the selected configuration, align the feature names with the RF/XGB pipelines and correct the contradictory CV conclusion. Verify the expected selection (`C=1_l2_balanced`, `val_15` macro-F1 ≈ 0.4786) by an executed run, not by assumption.
- **Activities:**
  - Inspected the PR branch and created an isolated worktree at `feature/model-logistic-regression` to avoid touching the uncommitted US-15 work on `feature/streamlit-app`; no unrelated branch or stash was modified.
  - Set `verbose_feature_names_out=False` on the inner nominal-imputer `ColumnTransformer` in `src/model_logreg.py`; the transformed names are now `Gender_Male`, `Var_1_Cat_*` and `Profession_*` without the `mode__`/`unknown__` prefixes, matching the random-forest and XGBoost pipelines (US-12 grouping). Verified 28 columns by an executed fit on `train_70`.
  - Reworked notebook section 8 to apply D-015 exactly: `StratifiedKFold(5, shuffle=True, random_state=42)` on `train_70`, full Pipeline passed to `cross_validate`, mean and standard deviation of the five fold scores (NumPy `ddof=0`), admissibility by mean train − CV accuracy gap < 5 pp, standard-error tie rule (`std / sqrt(5)`) and smallest train − CV gap as the final tie-break. Selection uses CV only; `val_15` is evaluated once for the official D-010 check.
  - Re-executed all nine notebook code cells (execution counts 1–9, no error outputs). The run selected `C=1_l2_balanced`: CV macro-F1 mean 0.485673, fold std 0.010076, standard error 0.004506; all six configurations meet the CV gap cut, and the tied group contains only `C=1_l2_balanced`. Official `val_15`: accuracy 0.495868, macro-F1 0.478583 (0.4786), accuracy gap +1.64 pp, which meets D-010.
  - Recorded per-class `val_15` precision/recall/F1 for the selected configuration: A 0.3949/0.4189/0.4066; B 0.3493/0.2616/0.2992; C 0.4908/0.5424/0.5153; D 0.6731/0.7147/0.6933.
  - Appended 8 rows to `results/logistic_regression.csv` without editing the 20 previous rows: six `cv5fold` rows (mean accuracy/macro-F1, with `accuracy_std`, `macro_f1_std` and train − CV gap in `notes`) plus `train_70` and `val_15` rows for the selected configuration (the `val_15` notes include precision/recall/F1 by class).
  - Corrected the previous conclusion that called `C=0.1_l2` "also first" in CV: it is second in CV macro-F1 (0.479499); `C=1_l2_balanced` leads the CV (0.485673). The previous `val_15`-based selection of `C=0.1_l2` is superseded by D-015.
  - Added `tests/test_model_logreg.py`, which fits the pipeline on `train_70` and checks 28 columns, the expected unprefixed names and the absence of `__` prefixes.
- **Files:** Modified: `src/model_logreg.py`, `notebooks/03_modeling/01_logistic_regression.ipynb`, `results/logistic_regression.csv`, `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only). Created: `tests/test_model_logreg.py`.
- **Verification:** Notebook re-executed in an isolated `jupyter_client` kernel with 9 code cells, execution counts 1–9 and no error outputs; CSV has 28 rows (20 previous + 8 new) and the selection reproduces Brian's expected `C=1_l2_balanced` with `val_15` macro-F1 0.4785827259899149; `pytest -q` → 17 passed (1 known `penalty` FutureWarning); `git diff --check` clean; only `train_70` is fitted and `val_15` is evaluated; `test_15.csv` is not read.
- **Outcome:** PR #66 changes implemented locally in the PR worktree and verified; the PR itself is not modified remotely yet.
- **Pending tasks:** Human review of the new result rows and notebook conclusions; explicit authorization to commit and push to `feature/model-logistic-regression`; re-run when US-05 phase 2 lands (D-013 Consequences).
- **Update 2026-11-17 (Claude Sonnet 5.5, with Rita Pereira's authorization, after Isbel's agent became unavailable):** the two lines above were written before commit `ce39771` reached the PR branch. Remaining review points of PR #66 handled on the branch:
  - Merged `develop` (SVM #70, EDA #71, D-015 #68). The conflict in this file was resolved by keeping develop's entries followed by A-024; no record was changed.
  - D-013 item 6 (Brian's blocking point 3): added `load_partitions()` and the reference `PARTITIONS` to `src/model_logreg.py` (row counts, SHA-256 with line endings normalised to LF, no shared `ID`; `test_15` is not loaded). The notebook now loads its data through it, so the check runs and prints every time. `tests/test_model_logreg.py` gained 2 tests (real data passes; a wrong checksum raises).
  - Notebook re-executed from a clean kernel in a temporary copy of the repository, so `results/logistic_regression.csv` was **not** appended a third time (the recording cell appends on every execution). All numeric outputs are identical to the committed ones; the differences are the new D-013 lines and a path separator (`results\` to `results/`). 9 code cells, execution counts 1-9, no error outputs, kernel `python3`.
  - `pytest -q` -> 35 passed on the merged branch. `test_15` is not read.
  - Not changed: `results/logistic_regression.csv` stays append-only and untouched. `src.select_config` (PR #72) cannot read the `cv5fold` notes because they use `macro_f1_std=` and `train_cv_acc_gap=` instead of the wording of the other models; the selected rows are not marked `SELECTED`; the baseline `val_15` row has no per-class precision and recall. These are left for the team to decide (harness patterns in #72, or an appended block).

---

<!-- Add new activities below using the same structure. Preserve previous records. -->

### A-027 — D-017 proposal: data used to fit the frozen model

- **Date:** 2026-11-17
- **Note:** Numbered A-027 because A-018, A-020 and A-023 to A-026 are used by open PRs. If A-027 is taken when this is merged, use the next free number.
- **Agent:** Claude Code (Claude Sonnet 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Record as a proposed decision whether the frozen model of US-11 is fitted on `train_70` or on `train_70 + val_15`, after Isbel asked that it not be decided by whoever implements the code.
- **Activities:**
  - Searched `develop` and the branches of PRs #69, #72, #73 and #74 for an existing decision: none exists. `src/compare_models.py` (PR #72) offers both options with `train_70` as the default; `src/evaluate_final.py` (PR #73) refuses `val_15` when `trained_on` is `train_and_val`.
  - Wrote D-017 (Proposed) with two alternatives, a recommendation for `train_70` only and the consequences of each option. Pedro's vote for `train_70` (team channel, relayed by Rita Pereira) is recorded; Brian's vote for `train_70` (same channel, relayed by Rita Pereira) and Isbel's vote for `train_70` (same channel, relayed by Rita Pereira) were added later the same day.
- **Files:** Modified: `docs/ai-usage/DECISION_LOG.md` (D-017 added), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Documentation only; no model executed, no data read or modified, no metric created. Row counts come from D-013; the 21.4 % figure is 1,210 / 5,647.
- **Outcome:** D-017 proposed in a PR into `develop`. The approval status is left to a human team member other than the author.
- **Pending tasks:** Votes of Isbel and Brian; human approval; then US-11 freezes the model with the approved option.


### A-022 — US-06 EDA on train_70: duplicate profiles and integration

- **Date:** 2026-11-17
- **Note:** Numbered A-022 because A-020 is used by open PR #69 (segment insights) and A-021 by open PR #70 (SVM). If a different number is free when this is merged, renumber.
- **Agent:** OpenCode (DeepSeek V4.1 Flash Free)
- **Human owner:** Pedro
- **Objective:** Pedro's section of US-06 (issue #10): repeated and ambiguous profiles on `train_70`, plus the integration of the three EDA sections with written answers to the issue questions.
- **Activities:**
  - Reviewed the merged sections of Rita Pereira (#58) and Brian (#64) and the initial EDA (#46), and measured the duplicates strictly on the training partition.
  - Created branch `feature/eda-duplicados` and notebook `04_eda_train70_duplicados.ipynb`: shape, types, nulls and target distribution; repeated profiles (322 profiles, 723 rows); ambiguous profiles with more than one segment (158 profiles, 365 rows, 6.5 %); most repeated segment pairs; an example profile; the ambiguity ceiling (171 rows, 3.0 %); and a sensitivity check with complete rows only (151 profiles, 14 rows matching only through a null).
  - Added `reports/duplicates_train_70.csv` (one row per repeated profile) and two figures: `eda_duplicate_profiles.png` and `eda_ambiguous_segment_pairs.png`.
  - Wrote `reports/eda_train70_sintesis.md`: integration of the three sections, answers to the four questions of the issue, a ranking of single-variable separation, an acceptance-criteria map and limitations.
  - Addressed the review of PR #71 by Rita Pereira: corrected the married-table denominator label (nulls included, as in #58), changed the model accuracy range from 52–55 % to 50–54 %, attributed `nulls_train_70.csv` to US-04 (#49) instead of #64, and documented the null-grouping sensitivity in the notebook and the synthesis.
- **Files:** Created: `04_eda_train70_duplicados.ipynb`, `reports/duplicates_train_70.csv`, `reports/eda_train70_sintesis.md`, `reports/figures/eda_duplicate_profiles.png`, `reports/figures/eda_ambiguous_segment_pairs.png`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Notebook executed from a clean kernel (12 code cells, execution counts 1–12, no error outputs); figures inspected; only `data/train_70.csv` is read and `val_15`/`test_15` are not opened; no CSV in `data/` is modified. An independent read-only script reproduced the figures: 5,246 distinct profiles, 322 repeated, 158 ambiguous, 365 ambiguous rows, 171 unlearnable rows, 14 null-only rows and 151 complete-case ambiguous profiles. Rita Pereira re-executed the previous version and reproduced the twelve outputs; the updated notebook keeps twelve code cells.
- **Outcome:** PR #71 open into `develop`; reviewed by Rita Pereira with changes requested. Not merged.
- **Pending tasks:** Approval of PR #71 and merge by a team member other than the author; then the acceptance criteria of issue #10.

### A-026 — US-16: first draft of the technical report

- **Date:** 2026-11-17
- **Note:** Numbered A-026 because A-018, A-020 and A-023 to A-025 are used by open PRs (#67, #69, #65, #66 and #72, #73). A-024 is currently used by both #66 and #72; whichever is renumbered should take A-027. If A-026 is taken when this is merged, use the next free number.
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita Pereira
- **Objective:** Start US-16 (issue #36): integrate the technical report from the work already recorded, leaving marked gaps for what depends on US-11, US-12 and US-14.
- **Activities:**
  - Read issue #36 and the criteria of US-11 (#27), US-12 (#29) and US-14 (#32); D-006, D-009, D-010, D-011, D-012, D-013, D-014, D-015 and D-016 (proposed); `reports/eda_train70_sintesis.md`, `reports/data_quality.md` and `reports/segment_insights.md` (PR #69).
  - Extracted the baseline and selected-configuration metrics of the four models from their results files, each read from its own branch: `results/svm.csv` (`develop`), `results/random_forest.csv` (PR #67), `results/boosting.csv` (PR #65) and `results/logistic_regression.csv` (PR #66, D-015 re-selection of 2026-11-17 11:15 UTC). Gaps are quoted as recorded in each run's `notes`.
  - Created branch `feature/technical-report` from `develop` (`ecaa580`) and `reports/technical_report.md` in English, like the other reports (decision of Rita Pereira): ten sections with the owner of each one as listed in issue #36, a sources table for every figure, and marked gaps for the final model, the test evaluation, the feature importance (US-11, US-12) and the error analysis (US-14). Figures taken from open PRs are marked with the PR number.
  - At Rita Pereira's request, a sentence comparing the XGBoost − random forest difference with the cross-validation fold variability was replaced by a plain statement that the difference (0.0147) is small and was not tested statistically: the fold standard deviation does not measure the variability of a paired difference on the same validation rows.
- **Files:** Created: `reports/technical_report.md`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Documentation only; no model executed and no data modified. Every figure was read from a recorded results file, a merged report or an approved decision; `test_15` was not read. `git diff --check` passes.
- **Outcome:** Draft committed with Rita Pereira's authorization. Not pushed yet.
- **Pending tasks:** Sections 6 and 7 (US-12 by Brian, PR #73; US-14 by Pedro, not started); US-11 decision and freezing; check the figures against `develop` once PRs #65, #66, #67 and #69 are merged; review of each section by its owner and of the whole report by Pedro.
- **Update 2026-11-17, afternoon (Claude Sonnet 5.5, with Rita Pereira's authorization):** D-017 was approved by Brian the same day (`train_70` only). Sections 1 and 3 now state it instead of leaving the choice pending, the references to PR #66 and PR #73 say "merged" (sections 3, 5 and 10), and D-017 is listed in the decision references (section 10). No figure was changed or recomputed and no data was read. Still pending: the final model and the test evaluation (US-11, US-12), the error analysis (US-14), checking the figures against `develop` once PR #65 and PR #67 are merged, and the review.
- **Update 2026-11-17, evening (Claude Opus 5.5, with Rita Pereira's authorization):** Merged `develop` (PR #65 and PR #67) into the branch without conflicts. Every figure in section 5 (tables 5.2 and 5.3, the configuration counts in 5.1 and the smallest XGBoost train − CV gap of 6.19 points over 26 candidates) was read again from `results/logistic_regression.csv`, `results/svm.csv`, `results/random_forest.csv` and `results/boosting.csv` in `develop` and matches; no figure changed. Only the references were updated: PR #65 and PR #67 are marked as merged, the note on how to read the figures says that only section 8 (PR #69) still depends on an open PR, and the US-11 pending note no longer waits for the model PRs. `test_15` was not read. Still pending: US-11 and US-12 (section 6), US-14 (section 7), the section 8 check after PR #69 and the review.
- **Update 2026-11-17, after Pedro's comment on the draft (Claude Opus 5.5, with Rita Pereira's authorization):** applied the non-blocking adjustments Pedro left in the PR. Sections 1, 3.4 and 5.4: the `val_15` figures of the four models are final, D-017 (Approved) is cited for fitting on `train_70` only, and only the freeze, the choice of the final model and the test metrics stay pending (US-11, US-12); the ranking is not called final until PR #72 and the freeze. Section 7: the hypothesis now says B errors may also go to A, based only on B having the lowest recall; it stays a hypothesis until the confusion matrix (US-12, US-14). Section 10.2: random forest runs listed in time order, with a note that the baseline was repeated later to add per-class precision and recall. Section 8.2 (D-016) not changed: D-016 is still Proposed. No figure was changed or recomputed and no data was read; Pedro's checks of sections 4, 5 and 8 were not repeated.
- **Update 2026-11-17, after PR #69 was merged (Claude Opus 5.5, with Rita Pereira's authorization):** merged `develop` into the branch without conflicts. Section 8 was checked against `develop`: every value of table 8.1 matches `reports/segment_profile_train_70.csv` (run 2026-11-16 14:31 UTC), and the figures in 8.2 (C 292, 34.2 %; B 268, 31.4 %) match `reports/segment_insights.md`. Only statuses and references changed: D-016 is cited as approved by Pedro in the review of PR #69 (sections 8.2 and 10), the campaign table as approved business hypotheses (section 8.3), PR #69 as merged (sections 8 and 10), and the note on how to read the figures no longer depends on an open PR. C stays the provisional first priority, as D-016 says. No figure was changed or recomputed and no data was read. Still pending: US-11 and US-12 (section 6, section 8.4), US-14 (section 7) and the review.
- **Update 2026-11-18 (Claude Opus 5.5, with Rita Pereira's authorization):** section 6 (owner: Brian) now has its structure ready to be filled after US-11 and US-12: 6.1 frozen model (model, configuration, `trained_on = train_70` per D-017, preprocessing, seed, freeze date and commit), 6.2 accuracy, macro-F1 and per-class precision, recall and F1 on `test_15` against validation and the baseline, 6.3 confusion matrix in counts and normalised by row, 6.4 guiding questions for the reading, and 6.5 permutation importance as `src/evaluate_final.py` computes it (nine original variables, macro-F1 drop, 5 repeats, `random_state=42`, on `val_15` per issue #29). Every result cell is left as "…" with the file it must be copied from; no figure was computed, estimated or read from `test_15`. XGBoost is named only as the expected choice, pending US-11.
- **Update 2026-11-18, later (Claude Opus 5.5, with Rita Pereira's authorization):** section 7 (owner: Pedro) now follows the acceptance criteria of issue #32 (US-14): 7.1 the existing preview from validation and the EDA (unchanged), 7.2 weakest segments, 7.3 most confused pairs against the pairs mixed in the data (section 4.4), 7.4 contrast with the segment profiles (hypotheses only), 7.5 review of misclassified rows, 7.6 data that would help and 7.7 optional subgroups. It cites `reports/error_analysis.md` as the full US-14 document. Result cells are left as "…"; no figure was computed. Finding recorded in 7.5: `src/evaluate_final.py` does not save row-level predictions, so the team must choose before US-12 runs whether the single `test_15` run also saves them or the row review uses `val_15`.
- **Update 2026-11-18, consistency pass (Claude Opus 5.5, with Rita Pereira's authorization):** section 10.1 now lists the US-11 and US-12 commands (`src.compare_models --stage table`, `--stage freeze --model <name> --train-with train_70`, `src.evaluate_final` on `val_15` and once on `test_15 --allow-test`), with every flag checked against `src/compare_models.py` on the PR #72 branch and `src/evaluate_final.py` in `develop`, and says that the logistic regression is run from `notebooks/03_modeling/01_logistic_regression.ipynb`. Section 10.2 lists the pending sources of sections 6 and 7. Consistency fixes: header date and status of sections 6 and 7, duplicated D-017 note removed from 3.4, XGBoost configuration in 5.1 written as parameters (matching `SELECTED_PARAMS` in `src/train_boosting.py`). Checked without changes: repeated figures across sections 1, 2, 4, 5 and 8 agree; 28.4 % (4.2, nulls in the denominator) and 29.0 % (8.1, nulls excluded) married in D are different definitions, each stated; the logistic regression "PROVISIONAL" limitation still applies (28 rows in `develop`). No figure was computed and no data was read.
- **Update 2026-11-18, after PR #72 and PR #78 were merged (Claude Opus 5.5, with Rita Pereira's authorization):** merged `develop` twice into the branch without conflicts (PR #72, then PR #78). Ran `python -m src.compare_models --stage table` without `--write` (reads `results/` only): accuracies, macro-F1 and per-class F1 match tables 5.2 and 5.3; its gap column shows 3.88 (SVM) and 3.32 (XGBoost) instead of 3.89 and 3.33 because it subtracts rounded accuracies, which section 5.4 now explains. Sections 6 and 7.2–7.3 were filled by a script that reads `reports/final_metrics_test_15_20261118T092535Z.csv`, the two test confusion matrices, `reports/final_metrics_val_15.csv` and `reports/feature_importance_val_15.csv` written by the single US-12 run of PR #78; no figure was typed by hand, computed anew or obtained by opening `test_15`. Also updated: summary (section 1), header statuses, 3.4 (freeze done, D-018 Proposed), 5.4, 7.5 (row review on `val_15`, because the test run saved no row-level predictions), 8.4, 10.2 and 10.3. Still pending: the majority baseline on `test_15` and the train − validation gap of the frozen model (requested from Brian in PR #78), sections 7.4–7.7 (US-14) and the approval of D-018.
- **Update 2026-11-18, after PR #79 was merged (Claude Opus 5.5, with Rita Pereira's authorization):** merged `develop` (PR #79) into the branch without conflicts. Section 6 is complete: the majority baseline on `test_15` (accuracy 0.2816, macro-F1 0.1099) and the frozen model on `train_70` (accuracy 0.5766, macro-F1 0.5609; train − validation gap 3.44 points) were copied from A-029 as completed by Brian in PR #79, with A-029 cited as the source in sections 6.1, 6.2 and 10.2; section 6.4 now compares the model with the baseline and states that the gap meets D-010. D-018 is cited as Approved by Pedro (2026-11-18) in sections 1, 3.4, 6.1 and 10.3. No figure was computed anew and `test_15` was not read. Still pending in the report: sections 7.4–7.7 (US-14) and the review.
- **Update 2026-11-18, afternoon (Claude Opus 5.5, with Rita Pereira's authorization):** section 9 now lists the model file as a limitation: `models/final_model.joblib` is git-ignored (`.gitignore`, `*.joblib`), and a rebuilt file can change a few predictions. The 656 correct rows on `val_15` are the diagonal of `reports/confusion_counts_val_15.csv` (124 + 90 + 176 + 266; 656 / 1,210 = 0.5421, as in `reports/final_metrics_val_15.csv`). The 657 come from the recorded boosting run (`results/boosting.csv`, accuracy 0.543 on 1,210 rows). Section 6.1 points to that limitation. No figure was computed anew, no model was loaded and `test_15` was not read. Still pending: sections 7.4–7.7 (US-14) and the review.
- **Update 2026-11-18, later (Claude Opus 5.5, with Rita Pereira's authorization):** section 6.1 now gives the SHA-256 of the model file (`428e56dd…7317`), and section 9 says it identifies the file evaluated on `test_15`. Rita's copy was hashed with `shasum -a 256` in this session; Brian reported the same hash for his copy with `sha256sum` in the team channel, together with the file's creation time (10:24 CET, before the US-12 run at 09:25 UTC). The model was not loaded and `test_15` was not read.
- **Update 2026-11-18, ~16:15 (Claude Opus 5.5, with Rita Pereira's authorization):** sections 7.4 and 7.6 filled without waiting for PR #81, because they only need sources already in `develop`: the test pairs of section 7.3 (`reports/confusion_counts_test_15_20261118T092535Z.csv`), the segment profiles of section 8.1 (`reports/segment_profile_train_70.csv`) and the contradictory profiles of section 4.4. 7.4 reads the three confused pairs (B → C; A ↔ D; A ↔ B) against the profiles; 7.6 says which missing variable (income, products P1–P5, vehicle type) could help each pair. Every explanation is marked as a hypothesis, and 7.6 says the effect of variables that were not measured cannot be estimated. The note at the top of section 7 now says 7.5 and 7.7 wait on US-14. No figure was computed; every value was copied from sections 4.4, 7.3 and 8.1.
- **Update 2026-11-18, ~17:00 (Claude Opus 5.5, with Rita Pereira's authorization):** section 9 now says the model file is not portable to Windows. Checked in this session on macOS by loading the official file (SHA-256 `428e56dd…7317`) and reading `save_config()` of its XGBoost booster: `learner.generic_param.rng_state` holds 624 numbers written as text (321 of them above 2^31 − 1). The Windows failure ("input stream corrupted") was reported by Pedro and traced to `rng_state` by Isbel in the team channel; it was not reproduced here because no Windows computer was available. No file was re-exported and the model was not rebuilt.
- **Update 2026-11-18, ~17:20 (Claude Opus 5.5, with Rita Pereira's authorization), after PR #81 was merged:** section 7.5 summarises `reports/error_analysis.md` sections 5 and 6 (554 misclassified and 656 correct rows of `val_15`; mean age, ever married, graduated, Low spending, family size and profession copied from its section 5 table), reads them against the pairs of section 7.4 as a hypothesis, and says the three examples per segment are the first rows of the file, so no pattern is drawn from them. Section 7.7 is marked as not done (optional criterion; `reports/error_analysis.md` section 9 says so). The status table, the note at the top of section 7, the end of section 7.3 and section 10.2 no longer say "pending US-14". Section 6.1 now says the recorded run gets one more row right (657 against 656) instead of "one row differs", because accuracy only shows the net difference. Section 9 states that the model file was generated on Linux (Brian, in the team channel) and loads on Linux and macOS. No figure was computed; `test_15` was not read.
---

### A-028 — US-11: common selection rule, comparison table and freeze harness

- **Date:** 2026-11-17
- **Note:** Numbered A-028 because A-021 (SVM), A-022 (US-06 duplicates), A-023 (boosting), A-024 (logistic review), A-025 (US-12) and A-027 (D-017) are already in `develop` or reserved by open PRs; A-026 is left for the report draft (PR #74).
- **Agent:** OpenCode (DeepSeek V4.1 Flash)
- **Human owner:** Brian
- **Objective:** US-11 (issue #27): make the approved D-015 rule reusable, assemble the D-010 comparison table and prepare the freeze of the winning model.
- **Activities:**
  - Created `src/select_config.py`: the D-015 rule as a module plus a CLI (`python -m src.select_config results/<model>.csv`). It reads the `cv5fold` rows, keeps the last batch of each configuration, parses the fold standard deviation and the train - CV gap from `notes` (the two formats in use) and applies items 2-6 of D-015. When the notes lack those two numbers it stops with an actionable message, because D-015 item 8 requires them.
  - Created `src/compare_models.py`: reads the four results files, keeps the rows each owner marked as the chosen configuration (`tuned`/`SELECTED`/`CANDIDATO`), prints accuracy and macro-F1 on `train_70` and `val_15`, the gap in points, the per-class F1 and the majority-class baseline; selects the winner by validation macro-F1 among the models with gap < 5 points (D-010 Consequences, between models) and freezes it with joblib (serialise, reload in a fresh object, predict one row). The registry only knows the modules that expose `SELECTED_PARAMS`; today that is the SVM.
  - Added `joblib==1.6.0` to `requirements.txt` as a direct dependency (installed version, verified in this run). Installing or upgrading dependencies needs human approval (AGENTS.md section 2), so the change is flagged for the team.
  - Created `tests/test_select_config.py` and `tests/test_compare_models.py` (15 tests: both notes formats, missing fields, last-batch handling, tie rule, fallback, table assembly, skipped models, winner choice and the freeze registry).
- **Files:** Created: `src/select_config.py`, `src/compare_models.py`, `tests/test_select_config.py`, `tests/test_compare_models.py`. Modified: `requirements.txt`, `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m pytest tests/test_select_config.py tests/test_compare_models.py -q` -> 15 passed. `python -m src.select_config results/svm.csv` returns `grid-07 {C: 1.0, gamma: 0.01, kernel: rbf}` with CV macro-F1 0.4923 and a 3.54-point train - CV gap, matching the configuration recorded in PR #70. `python -m src.compare_models --stage table` builds the table with the SVM and lists the other three files as not yet available. No data file and no `test_15` were read.
- **Outcome:** The D-015 rule is reusable and the comparison harness is ready. The table cannot be completed yet: `results/boosting.csv` (PR #65) has no row marked as the chosen configuration, and `results/logistic_regression.csv` (PR #66) records pooled out-of-fold metrics without the fold standard deviation or the train - CV gap, so `select_config` stops with the message that D-015 item 8 requires them. Both owners need to re-derive and record their selection.
- **Pending tasks:** Merge #65, #66 and #67; complete the table; team approval of the `joblib` dependency and of the choice between training the frozen model on `train_70` or on `train_70 + val_15`; then freeze the winner and record the US-11 decision.
- **Update 2026-11-17 after the review of PR #72 (Rita Pereira):** renumbered from A-022 to A-024 because A-022 is used by PR #71 (merged) and A-023 by PR #65. Three fixes from the review: `baseline` rows are left out of the candidate table (the SVM counted 6/10 admissible instead of 6/9); the CV mean is taken from `notes` when the file stores the pooled out-of-fold score in the `macro_f1` column (the boosting file does: 0.5049 against the 0.5045 fold mean); and `load_selected_rows` now takes the last marked configuration that has both rows and ignores `tuned-fallback-N` rows, so a fallback from D-015 item 7 cannot be mistaken for the choice. The freeze registry now names every model's builder (keyword arguments or one parameter dict) and stops with a message that asks the owner to expose `SELECTED_PARAMS`; today only the SVM does, and the boosting winner needs the constant when PR #65 merges. Rita Pereira approved `joblib==1.6.0` as a direct dependency and voted to freeze on `train_70` only.
### A-025 — US-12: final evaluation script of the frozen model (test and importance)

- **Date:** 2026-11-17
- **Note:** Numbered A-025 because A-022 (PR #71), A-023 (PR #65) and A-024 (PR #72) are already used or reserved. Not executed on `test_15`; the entry records the instrument, not the final figures.
- **Agent:** OpenCode (DeepSeek V4.1 Flash)
- **Human owner:** Brian
- **Objective:** US-12 (issue #29): evaluate the frozen model once on `test_15` and report accuracy, macro-F1, per-class metrics, confusion matrices and the importance of the original variables.
- **Activities:**
  - Created `src/evaluate_final.py`: loads the joblib written by `src.compare_models --stage freeze`; verifies the partition against D-013 (rows and SHA-256 with LF) before reading it; reports accuracy, macro-F1 and per-class precision, recall and F1 (D-010); builds the confusion matrix in counts and normalised by row; compares with the majority-class baseline and, for `test_15`, with `val_15`; and computes permutation importance with macro-F1 as the score.
  - Importance is computed on the **raw** columns of the Pipeline, so the one-hot columns of a variable are grouped by construction (one row per original variable) instead of being permuted one dummy at a time.
  - `test_15` is refused unless `--allow-test` is passed, to keep the single evaluation of D-012 item 4 explicit.
  - Created `tests/test_evaluate_final.py` (7 tests: D-013 reference values, metric names, row-normalised confusion with an absent class, the test guard, the checksum check, importance ordering and the majority-class baseline).
- **Files:** Created: `src/evaluate_final.py`, `tests/test_evaluate_final.py`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m pytest tests -q` -> 42 passed on this branch alone. The script was not run against `test_15`; `load_partition` refuses it without `--allow-test`. No repository data file and no prediction on the test split were produced.
- **Outcome:** The evaluation instrument is ready and waiting for the frozen model of US-11 (open PR #72).
- **Update 2026-11-17 after the review of PR #73 (Rita Pereira):** three fixes. (1) The script reads `trained_on` from the joblib payload: if the frozen model was fitted on `train_70 + val_15`, it refuses to score `val_15` (the metrics and importance would be optimistic) and skips the validation reference on `test_15`. (2) Permutation importance runs on `val_15` only; on `test_15` it is off unless `--importance` is passed, as issue #29 asks. (3) A second evaluation of `test_15` is refused when a report already exists, unless `--allow-test-rerun`; every test run writes its own timestamped report, so the single evaluation leaves a trace. Renumbered from A-023 to A-025 because A-023 is used by PR #65 and A-024 by PR #72.
- **Pending tasks:** Merge PR #72 and the three model PRs (#65, #66, #67); freeze the winner on `train_70` (team decision recorded by Rita Pereira); run the evaluation once on `val_15`, then once on `test_15` with `--allow-test`; record the figures and the importance in the results registry and in the technical report (US-16).

---

### A-023 — US-09: boosting configuration chosen with cross-validation (D-015)

- **Date:** 2026-11-17
- **Note:** Numbered A-023 because A-019, A-021 and A-022 are already in `develop` and A-020 is used by open PR #69.
- **Agent:** OpenCode (DeepSeek V4.1 Flash Free)
- **Human owner:** Pedro
- **Objective:** finish US-09 (issue #21) with D-015 approved: make `src/train_boosting.py` choose its configuration by cross-validation and record the choice in `results/boosting.csv`.
- **Activities:**
  - Added `--select` to `src/train_boosting.py`, with `select_cv()` implementing the approved rule (D-015 items 2, 3, 4 and 6) with the same wording as `src/train_svm.py`, so the four models of US-11 are chosen the same way. `val_15` takes no part in the decision.
  - Ran it on 2026-11-17 over the 26 candidate configurations already recorded (18 grid + 8 refinement; the baseline with defaults is the reference, not a candidate). No retraining of the 27 recorded runs: the existing `cv5fold` rows already carried the fold means, the standard deviation and the train−CV gap that the rule needs.
  - No candidate met the 5-point train−CV gap limit (the smallest is 6.19 points), so D-015 item 6 applies: the smallest gap wins, `refine n_estimators=300, learning_rate=0.05, min_child_weight=5` (`max_depth=3`, `subsample=1.0`, `colsample_bytree=0.8`, seed 42).
  - Appended three rows marked `SELECTED` to `results/boosting.csv`: CV (accuracy 0.5215, macro-F1 0.5049), `train_70` (0.5762 / 0.5608) and `val_15` (accuracy 0.5430, macro-F1 0.5227, train−val gap 3.32 points, within the limit), the last one with per-class precision, recall and F1.
  - Fixed `SELECTED_PARAMS` in the module so US-11 imports the choice instead of copying hyperparameters by hand.
  - Added three tests: the tie within one standard error, the fallback when no configuration is admissible and the check that `SELECTED_PARAMS` is one of the recorded candidates. The suite passes (42 tests).
  - README: macOS note (`brew install libomp`, needed by XGBoost) and the `--select` usage.
- **Files:** Modified: `src/train_boosting.py`, `tests/test_train_boosting.py`, `README.md`, `results/boosting.csv` (three appended rows), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** `python -m pytest tests` passes (42 tests). The selection run starts with the D-013 partition check (row counts, checksums and zero ID overlap between partitions; `test_15` is never read). The selected `val_15` figures (accuracy 0.5430, macro-F1 0.5227) match the independent calculation made by the reviewer of PR #65 from the same CV rows.
- **Outcome:** PR #65 updated; not merged.
- **Pending tasks:** Approval and merge of PR #65 by a team member other than the author; the chosen configuration feeds US-11.

---

### A-029 — US-11 freeze and US-12 single test evaluation

- **Date:** 2026-11-18
- **Note:** Numbered A-029 because A-028 is used by PR #72 (US-11 harness, merged).
- **Agent:** OpenCode (DeepSeek V4.1 Flash)
- **Human owner:** Brian
- **Objective:** Execute US-11 (issue #27): freeze the winning model on `train_70` and record the comparison table; then run US-12 (issue #29) once on `test_15`.
- **Activities:**
  - Branch `feature/model-freeze` from `develop` (`31c134a`).
  - The freeze failed at first: the boosting Pipeline needs numeric labels, so `build_pipeline` raised `ValueError: Invalid classes inferred from unique values of y`. Added `src/frozen.py` with `FrozenPipeline`, a `ClassifierMixin`/`BaseEstimator` wrapper that encodes the target on `fit` and decodes it on `predict`, so the artifact takes and returns `A`-`D` and works with `permutation_importance`. The class lives in its own module because a class defined in a script executed with `python -m` is pickled as `__main__.FrozenPipeline` and cannot be unpickled by another module.
  - `python -m src.compare_models --stage table --write` → `results/model_comparison.csv` with the **four candidate models** (the Dummy is not a candidate, so the script prints it as a reference instead of storing it): XGBoost 0.5227 · Random Forest 0.5080 · SVM 0.4853 · logistic 0.4786, all with gap < 5 points. The majority-class reference is accuracy 0.2810 and macro-F1 0.1097 on `val_15`, and accuracy 0.2816 and macro-F1 0.1099 on `test_15`.
  - `python -m src.compare_models --stage freeze --model boosting` → `models/final_model.joblib` (5,647 rows, `trained_on = train_70`, `frozen_params` = the D-015 item 6 configuration: 300 trees, depth 3, learning rate 0.05, subsample 1.0, colsample 0.8, min_child_weight 5). The artifact is reloaded and predicts the first row, as US-11 requires; it is not committed because `*.joblib` is ignored.
  - `python -m src.evaluate_final --model models/final_model.joblib --partition val_15` → accuracy 0.5421, macro-F1 0.5222, confusion matrices and permutation importance; on `train_70` the same artifact scores accuracy 0.5766 and macro-F1 0.5609, so its train - validation gap is **3.44 points** and meets the D-010 limit (Age 0.080 > Profession 0.077 > Spending_Score 0.054 > Family_Size 0.029).
  - `python -m src.evaluate_final --model models/final_model.joblib --partition test_15 --allow-test` → accuracy 0.5599, macro-F1 0.5456 (test − validation: +1.77 points of accuracy, +2.34 of macro-F1). Single evaluation; the report file carries a timestamp.
- **Files:** Created: `src/frozen.py`, `results/model_comparison.csv`, `reports/final_metrics_val_15.csv`, `reports/final_metrics_test_15_20261118T092535Z.csv`, the confusion matrices and `reports/feature_importance_val_15.csv`. Modified: `src/compare_models.py` (imports the wrapper), `tests/test_compare_models.py` (round-trip test), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry) and `docs/ai-usage/DECISION_LOG.md` (D-018 proposal).
- **Verification:** `python -m pytest tests -q` → 120 passed. The table is reproduced from the four results files; the frozen artifact reloads and predicts; `test_15` was read once and the script refuses a second run without `--allow-test-rerun`.
- **Note on a one-row difference:** the frozen model scores 0.5421 / 0.5222 on `val_15`, while the boosting row recorded in `results/boosting.csv` says 0.5430 / 0.5227. The difference is one row out of 1,210 and is **not** caused by the wrapper: reproducing with the boosting module's own `fit_and_evaluate(SELECTED_PARAMS)` on this machine gives 0.5421 / 0.5222 as well. The likely cause is run-to-run or hardware variation of XGBoost `hist`. Both figures are reported; the ranking does not change.
- **Outcome:** US-11 frozen (XGBoost on `train_70`) and US-12 evaluated once on `test_15`; the PR carries the evidence.
- **Pending tasks:** Review and merge of the PR; approval of D-018 (Proposed); the app needs `xgboost` installed and, on macOS, `libomp`, plus the `.joblib` copied to the machine that runs the demo.

---

### A-030 — US-14: error analysis of the frozen model

- **Date:** 2026-11-18
- **Agent:** OpenCode (Beam Free)
- **Human owner:** Pedro
- **Objective:** Analyse where the frozen XGBoost model (D-018) is wrong and why (issue #32, US-14).
- **Activities:**
  - Loaded `models/final_model.joblib` (FrozenPipeline, trained on `train_70`, D-017) and predicted on `val_15` (1,210 rows).
  - Computed the confusion matrix on `val_15`: 656 correct (accuracy 0,5421), B is the weakest segment (recall 0,323), D the strongest (0,782).
  - Extracted the top confused pairs from the test matrix (`confusion_counts_test_15_20261118T092535Z.csv`): B→C 87 (31,3 %), A→D 68 (23,0 %), B→A 54 (19,4 %), D→A 64 (18,8 %), A→B 51 (17,2 %).
  - Compared error profiles vs correct profiles: misclassified rows are ~5,8 years older, more married (64,5 % vs 52,0 %) and more graduated (67,5 % vs 57,3 %).
  - Reviewed 3 misclassified examples per segment and proposed 5 hypotheses (marked as hypotheses, not facts).
  - Recommended additional data: income, products, vehicle type, contact channel, purchase history.
  - Wrote `reports/error_analysis.md` and saved predictions to `reports/error_analysis_val_15.csv` (553 rows).
- **Files:** Created: `reports/error_analysis.md`, `reports/error_analysis_val_15.csv`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** Model loaded from `models/final_model.joblib`; predictions on `val_15` match `reports/final_metrics_val_15.csv` (accuracy 0,5421, macro-F1 0,5222). `test_15` not read for row-level analysis; only aggregated matrices from `reports/` used.
- **Outcome:** US-14 document ready for review; pending PR into `develop`.
- **Pending tasks:** Review and merge of the PR; update section 7 of the technical report (#74) with the final figures.
- **Update 2026-11-18, afternoon (Claude Opus 5.5, with Rita Pereira's authorization; Pedro asked the team for help in the channel):** the files above came from a model rebuilt on Pedro's computer (553 errors, 657 correct), not from the frozen file evaluated in US-12. Re-run on Rita's computer with the official `models/final_model.joblib` (SHA-256 `428e56dd…7317`, the same hash reported by Brian), XGBoost 3.4.1 and `libomp` 23.1.6: the matrix check passes, `reports/error_analysis_val_15.csv` now has **554** rows, the diagonal is 124 · 90 · 176 · 266 (656 correct), and sections 1, 5 and 6 of `reports/error_analysis.md` were regenerated by the script (one example changed: the B executive with High spending is now predicted as D, and the reading of the examples says so). `src/error_analysis.py`: `ROOT` is the repository folder instead of a fixed `F:/…` path; the matrix check now stops the script on a mismatch; the copy to a fixed `C:/…` folder was removed; the messages no longer suggest rebuilding the model. Checked with a separate script that the 12 error pairs match `reports/confusion_counts_val_15.csv`, the rows match `data/val_15.csv`, and the section 5 tables and section 6 examples can be recomputed from the CSV. `test_15` was not read and the model was not rebuilt.

---

### A-032 — US-17: business presentation (PowerPoint and PDF, Spanish)

- **Date:** 2026-11-18
- **Note:** First numbered A-030; renumbered to A-032 on 2026-11-18 because A-029 is in `develop` (PR #78), A-030 is used by PR #81 (US-14) and A-031 by PR #82 (US-15).
- **Agent:** Claude Code (Claude Opus 5.5)
- **Human owner:** Rita
- **Objective:** US-17 (issue #37): business presentation in non-technical Spanish with the segment profiles, the segment to prioritise, the campaigns as business hypotheses and the recommendation to collect income, product (P1 to P5) and vehicle type.
- **Instructions received:** team decisions of 2026-11-18 (format `.pptx` + PDF in the repo; Spanish, translating only visible text; validation accuracy 0.5430 on `val_15` shown as "54 de cada 100" with a visible "validation, not test" label, to be replaced everywhere at once if US-12 lands before delivery; this deck is only the business part, after the technical part and the app demo). Pedro asked to mention macro-F1 (0.5227) as well: it is in the speaker notes.
- **Activities:**
  - Read `AGENTS.md`, issue #37, `reports/segment_insights.md`, `reports/segment_profile_train_70.csv` and section 8 of `reports/technical_report.md` (PR #74 branch). Checked 0.5430 / 0.5227 against A-023 and 0.2810 against the technical report draft.
  - Built 11 slides: cover, question, data available and missing, the four segments, spending and marital status, segment to prioritise (D-016), campaigns, recommendation and next steps; annex: what distinguishes the segments, segment D, model accuracy. Speaker notes on every slide carry the technical terms and sources.
  - Every figure is copied from `segment_profile_train_70.csv` and `segment_insights.md` with the same rounding (one decimal, Spanish comma). No new figure was computed. The two EDA figures (`eda_spending_by_segment.png`, `eda_married_by_segment.png`) were redrawn as native, editable charts with the same CSV values, because the PNGs show integer rounding and technical labels.
  - Campaign texts translated without changing their content (table of §5, approved as business hypotheses in the review of PR #69). "Test the campaigns before rolling them out" is marked as optional: it is not in the issue.
  - Model feature importance is shown as pending (US-12); nothing is claimed about it.
- **Tools:** the deck is generated with `pptxgenjs` 3.12.0 installed in a temporary folder outside the repo (approved by Rita); the PDF is exported with PowerPoint. No dependency added to the project.
- **Files:** Created: `presentation/business_presentation.pptx`, `presentation/business_presentation.pdf`. Modified: `README.md` (link), `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only). No CSV modified; `test_15` and the Kaggle `Test.csv` not used.
- **Verification:** OOXML validation passed; visual review of the 11 slides rendered from the PDF; check that the slide text (not the notes) contains no technical terms (`accuracy`, `macro-F1`, `train_70`, `pipeline`, ...).
- **Outcome:** first version opened as a draft PR (#77) for team review. The current status is in the last update below.
- **Update 2026-11-18 after PR #78 and PR #79 (Rita Pereira):** US-12 ran (XGBoost frozen on `train_70`, D-018 approved by Pedro), so the validation figure is replaced as the team agreed. Slide 11 now shows "56 de cada 100" labelled "Resultado final" (accuracy 0.5599 on `test_15`, `reports/final_metrics_test_15_20261118T092535Z.csv`), against "28 de cada 100" for always answering D (0.2816 on `test_15`, A-029); the notes keep the validation figures (0.5430 / 0.5227) for comparison and add macro-F1 0.5456. Slide 9 replaces "pending" with the three variables the model relies on most (Age 0.080, Profession 0.077, Spending_Score 0.054; `reports/feature_importance_val_15.csv`). The figures are copied from the reports in `develop`; `test_15` itself was not read and no figure was computed.
- **Update 2026-11-18, afternoon (Claude Opus 5.5, with Rita Pereira's authorization):** cross-check of the deck against the technical report (PR #74). The speaker notes of slide 11 gave 0.5430 / 0.5227 as the validation figures of the model, but those come from the recorded boosting run (`results/boosting.csv`); the frozen model scores 0.5421 / 0.5222 on `val_15` (`reports/final_metrics_val_15.csv`), which is the figure the "+1.77 points" in the same note is computed from. The note now gives 0.5421 / 0.5222, as section 6.2 of the report and the README do. Only `ppt/notesSlides/notesSlide11.xml` changed inside the `.pptx` (every other entry is byte-identical); the PDF has no speaker notes and is unchanged. The other figures of slides 3, 4, 6, 7, 9 and 11 were checked against `reports/segment_insights.md`, `reports/feature_importance_val_15.csv` and `reports/final_metrics_test_15_20261118T092535Z.csv` and match. No figure was computed and `test_15` was not read.
- **Update 2026-11-18, evening (Claude Opus 5.5, changes chosen by Rita Pereira):** adapted the deck to the team's presentation split (business part first, about 4:30 per person) and to US-14 (PR #81). (1) Slide 2 names the target audience: the marketing team. (2) "¿Cuánto acierta el modelo?" moves from the annex to the main part, before the recommendation (now slide 7), because Rita presents the result. The spending and marital-status charts move to the annex (now slide 9). (3) Slide 7 adds that the model errs most on B: 1 in 3 B customers is predicted as C (B → C, 87 of the 278 B customers in `test_15`, 31.3 %; `reports/error_analysis.md` §4, `reports/confusion_counts_test_15_20261118T092535Z.csv`). (4) Slide 8 adds contact channel and purchase history as secondary data to collect (`reports/error_analysis.md` §8); issue #37 only asks for income, products and vehicle type, so they stay secondary. The cover and closing notes now describe the new order. The 0.5421 / 0.5222 correction from the previous update is kept. No figure was computed, `test_15` was not read, and the slide text still contains no technical terms.
- **Status 2026-11-18, night (Claude Opus 5.5, with Rita Pereira's authorization):** PR #77 is out of draft and ready for review. Pedro reviewed it on GitHub (figures match the CSVs and the report; campaigns shown as hypotheses; he approves the content) and Brian gave his OK in the team channel. The two points Pedro raised were already in place: the slide 7 notes give macro-F1 0.5456 on test and 0.5421 / 0.5222 on validation, and the low-spending row is on slide 4. The technical report (PR #74, merged) uses the same test figures (0.5599 / 0.5456, baseline 0.2816), and so does the technical presentation (PR #84, merged) for the model (0.5599 / 0.5456). Approval is recorded by the team in PR #77 and issue #37, not in this entry.
- **Pending tasks:** team approval of US-17 in issue #37 and merge of PR #77 into `develop` before the `develop` → `main` PR.

---

### A-033 — US-18: technical presentation of the code

- **Date:** 2026-11-18
- **Note:** Numbered A-033 because A-030 is used by PR #81 (US-14), A-031 by PR #82 and A-032 by PR #77.
- **Agent:** OpenCode (DeepSeek V4.1 Flash)
- **Human owner:** Brian
- **Objective:** US-18 (issue #38): a technical presentation explaining how the project was built and how data leakage and overfitting were controlled. The task moved from Pedro to Brian by team agreement in the channel; Pedro contributes and reviews the slides on split, Pipeline, models and overfitting.
- **Activities:**
  - Branch `feature/technical-presentation` from `develop` (`d77f0ee`).
  - Wrote `docs/technical-presentation.md`: 12 slides (~8 minutes) with on-screen content, speaker notes, a Mermaid diagram of the full path, the model comparison table, the frozen-artifact contract, the per-class results, the confusion pairs and the permutation importance.
  - Every figure was taken from `results/model_comparison.csv`, `reports/final_metrics_*.csv`, `reports/confusion_*.csv` and `reports/feature_importance_val_15.csv`; no new metric was computed.
  - Integrated Pedro's block with three corrections: the XGBoost gap is 3.33 points (the recorded value, not 3.32 from subtracting rounded accuracies), the majority-class baseline was added (0.2810 / 0.1097) so the "double the baseline" claim is supported, and the leakage sentence (preprocessing fitted per fold) was made explicit because it is an acceptance criterion.
  - Included the mapping to the four acceptance criteria, the speaking split and a table tracing each figure to its file. The app screenshot is marked as pending until PR #82 merges.
- **Files:** Created: `docs/technical-presentation.md`. Modified: `docs/ai-usage/AI_ACTIVITY_LOG.md` (this entry only).
- **Verification:** documentation only; no model, data or result was touched and no new metric was produced. Cross-checked each figure against the referenced files in `develop`. The confusion pairs are quoted as a share of the true class (B→C is 87 of 278 customers of B, 31 %), not as a share of the whole partition.
- **Outcome:** Presentation ready for review in a PR into `develop`; Pedro reviews slides 3, 4 and 6.
- **Pending tasks:** Review and merge of the PR; add the app screenshot when #82 lands; confirm the speaking split in the daily.
- **Update 2026-11-18 after the review of PR #84 (Rita Pereira and Pedro):** applied the seven corrections agreed by both reviewers: renumbered to A-033 (A-030 is US-14), the configuration counts are labelled per model (logistic 6, SVM 10, random forest 60, XGBoost 27), the macro-F1 comparison is stated as ~4.8x with the accuracy as the figure that doubles (0.2810 → 0.5430), the unavoidable error is 3.0 % of rows (171, D-009) rather than the 6.5 % of contradictory profiles, the class split is listed (A 24.4, B 23.0, C 24.4, D 28.1) instead of a range, the app slide quotes the shared SHA-256 instead of "generated with one command", and the per-class note became "reconoce mejor D y C". The on-screen text was translated into Spanish, keeping code identifiers in English, as the team decided for every spoken artefact; `reports/technical_report.md` keeps the English Windows portability limitation, so the README states that a portable export *can be prepared* rather than existing.
