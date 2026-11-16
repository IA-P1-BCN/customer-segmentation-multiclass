# AGENTS.md

## 1. Project Context

Collaborative Data Science and Machine Learning project: customer segmentation through multiclass classification, using demographic and behavioral customer data to predict customer segments. The work spans EDA, data cleaning and preprocessing, feature engineering, model development and comparison, evaluation and validation, a prediction application, and technical documentation plus a business-oriented presentation.

**Dataset** ([Kaggle – Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)):

- `Train.csv` — labeled data for EDA, preprocessing, model development and validation.
- `Test.csv` — separate test data; its structure and the availability of target labels must be verified before use.
- Target variable: `Segmentation` (multiclass; classes A, B, C and D).

**Data rules:**

- The original test data must never be used for training or for decisions that introduce data leakage.
- Any additional validation split must be created from the training data using an appropriate strategy.
- Data integrity must be preserved.

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

**Branches** — keep `main` stable; work on one branch per independent task, named:

- `feature/<description>` (new functionality), `fix/<description>` (bug fixes), `docs/<description>` (documentation), `refactor/<description>` (code restructuring).

**Commits** — use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`), with clear descriptive messages, each focused on a single logical change.

**Pull Requests** — required to integrate significant changes into `main`; explain purpose and scope, include relevant tests and validation results, and request human review before merging.

**Agent restrictions:** before starting any task, inspect the current branch and working tree (`git status`); preserve unrelated changes, including uncommitted work, and never overwrite another team member's work; never discard, reset, overwrite or delete existing work, and never use destructive Git commands, without explicit approval; never commit, push, merge or rebase without explicit human authorization; after completing a task, report the branch, changed files and validation status.

## 5. Technical Standards and Reproducibility

- Pin the Python environment (interpreter and package versions) so every result is reproducible; installing or upgrading dependencies requires human approval (see §2).
- Set and document random seeds for every stochastic step (splits, resampling, models) so runs can be repeated exactly.
- Define and justify the validation strategy before modeling and keep it consistent across all model comparisons; never tune against untouched test data.
- Fit preprocessing only on training data; keep transformations reproducible and versioned.
- Notebooks are expressly allowed for EDA, visualization and experimentation; prioritize scripts/modules for reusable logic and any process that must be rerun reproducibly.
- Every reported metric must come from an executed, recorded run — never estimated or remembered; log the run per §3.
