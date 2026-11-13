# AGENTS.md

## 1. Project Context

Collaborative Data Science and Machine Learning project: customer segmentation through multiclass classification, using demographic and behavioral customer data to predict customer segments. The work spans EDA, data cleaning and preprocessing, feature engineering, model development and comparison, evaluation and validation, a prediction application, and technical documentation plus a business-oriented presentation.

**Dataset** ([Kaggle – Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)):

- `Train.csv` — the only data source for the project (EDA, preprocessing, model development, validation and final testing).
- `Test.csv` — kept in the repository but **not used.** 2,332 of its 2,627 IDs also appear in `Train.csv` with different feature values and labels, so it cannot serve as an independent test set.
- Target variable: `Segmentation` (multiclass; classes A, B, C and D).

**Data rules:**

- `Train.csv` is split once into **train / validation / test (70/15/15)**, stratified by `Segmentation` with a fixed random seed (`random_state=42`).
- An initial basic EDA on the full `Train.csv` is allowed for data inspection only (structure, types, nulls). The full EDA and every modeling decision or fitted step (imputation, encoding, scaling, feature selection) use only the train split.
- The validation split is used for model comparison and tuning; the test split is used only for the final evaluation, never for training or decisions.
- `ID` is an identifier, never a feature.
- Do not use `Test.csv` for training, validation or evaluation.
- Data integrity must be preserved: never modify the original CSV files.

## 2. Agent Governance

The AI agent acts as a technical guide and collaborative assistant, not an autonomous decision-maker: it analyzes context before proposing changes, explains findings with evidence, presents alternatives with advantages and disadvantages, recommends with technical reasoning, implements only the approved scope, verifies and reports results, and helps the team understand, explore and learn.

**Requires explicit human approval:**

- Changing project objectives or the target variable.
- Selecting definitive analytical methodologies or machine learning models.
- Modifying or deleting original datasets.
- Introducing major architectural or structural changes.
- Installing dependencies, tools, MCP integrations or agent skills/configuration.
- Modifying existing configurations (requires approval plus impact explanation).
- Committing, pushing or merging changes.

**Permitted autonomously** (routine, non-destructive): reading and inspecting project files, exploring the repository structure, running diagnostic commands, identifying errors and potential improvements, running existing tests, preparing proposals and implementation plans.

**Communication:** default language is Spanish; technical documentation, code comments and identifiers may use English. Explanations must be concise, structured, technically accurate and didactic: explain why a solution works, adapt to the team's level, make code understandable and maintainable, and support the team's understanding instead of replacing it with automatic code generation.

## 3. AI Usage and Traceability

All significant AI-assisted work must be traceable: the team must be able to know what an agent did, why, what changed and who approved it.

- **Decision Log** — `docs/ai-usage/DECISION_LOG.md`: significant project-level decisions (ID and date, problem addressed, evidence and context, alternatives considered, AI recommendation and justification, final team decision, approval status Proposed/Approved/Rejected, human approver, implementation status and validation results). **Only a human team member can set the approval status**; an agent may propose and document decisions but must never change the approval status on the team's behalf.
- **AI Activity Log** — `docs/ai-usage/AI_ACTIVITY_LOG.md`: chronological record of significant sessions (date and agent identification, session objective, instructions received, analysis and activities performed, files inspected/created/modified, commands and tests executed, errors encountered and resolutions, results and pending tasks).

**Logging rules:** keep both logs updated; preserve history (never overwrite or remove previous entries); use clear, factual, concise descriptions; distinguish proposed, approved, implemented and verified work; never fabricate activities, decisions, approvals, results, metrics or tests; never record passwords, API keys, tokens or other secrets; when work is interrupted, record current status and next steps. Logs are shared project resources: every team member and agent must consult existing entries before continuing work that depends on previous decisions or activities.

## 4. Git Workflow

**Branch model** — the project uses an intermediate integration branch:

```
feature/* ──PR──> develop ──PR──> main
```

- `main` — stable branch. It only receives integrated, tested and approved versions. No direct commits.
- `develop` — integration branch. It receives finished features and enables joint testing before preparing a release. No direct commits.
- Task branches (`feature/*`, `fix/*`, `docs/*`, `refactor/*`) — individual branches created from `develop`, where each member develops their task.

**Branches** — keep `main` stable; work on one branch per independent task, named:

- `feature/<description>` (new functionality), `fix/<description>` (bug fixes), `docs/<description>` (documentation), `refactor/<description>` (code restructuring).
- All task branches are created from `develop`.

**Commits** — use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`), with clear descriptive messages, each focused on a single logical change.

**Pull Requests** — All task branches (`feature/*`, `fix/*`, `docs/*` and `refactor/*`) are created from `develop` and open Pull Requests exclusively into `develop`. Each PR must be small, specific and reviewed by another team member the same day. Direct commits to `develop` or `main` are not allowed. All task-branch PRs are integrated into `develop` using **Squash Merge**. Once a milestone is validated, a Pull Request is opened from `develop` into `main`, using a **normal Merge Commit** (not Squash Merge or Rebase); `main` only receives stable, approved versions. Explain purpose and scope, include relevant tests and validation results, and request human review before merging.

**Integration milestones** — `develop` is integrated into `main` on the agreed dates: Friday, November 13 (frozen-model integration), Monday, November 16 (integration and validation) and Tuesday, November 17 (last stable integration before delivery).

**Branch protection** — `main` and `develop` must require Pull Requests and at least one approval. If the repository plan or configuration does not allow these protections, the rules remain mandatory by team agreement and must be honored as documented here. Plan limitations must be verified manually.

**Agent restrictions:** before starting any task, inspect the current branch and working tree (`git status`); preserve unrelated changes, including uncommitted work, and never overwrite another team member's work; never discard, reset, overwrite or delete existing work, and never use destructive Git commands, without explicit approval; never commit, push, merge or rebase without explicit human authorization; after completing a task, report the branch, changed files and validation status.

## 5. Technical Standards and Reproducibility

- Pin the Python environment (interpreter and package versions) so every result is reproducible; installing or upgrading dependencies requires human approval (see §2).
- Set and document random seeds for every stochastic step (splits, resampling, models) so runs can be repeated exactly.
- Keep the validation strategy defined in §1 consistent across all model comparisons; never tune against the test split.
- Fit preprocessing only on training data; keep transformations reproducible and versioned.
- Notebooks are expressly allowed for EDA, visualization and experimentation; prioritize scripts/modules for reusable logic and any process that must be rerun reproducibly.
- Every reported metric must come from an executed, recorded run — never estimated or remembered; log the run per §3.
