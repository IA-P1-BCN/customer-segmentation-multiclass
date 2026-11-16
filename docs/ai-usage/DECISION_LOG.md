# Decision Log

## Purpose

This document records significant project decisions to maintain transparency, consistency and shared context across the team and its AI agents.

Only decisions that affect the project's objectives, methodology, architecture, tools or development workflow should be recorded.

Routine tasks, minor code changes and temporary troubleshooting do not require entries.

## Decision Status

- **Proposed:** Suggested but not yet approved.
- **Approved:** Explicitly approved by a human team member.
- **Rejected:** Reviewed and explicitly rejected by a human team member.

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

### D-007 — Collaborative workflow and dataset management

- **Date:** 2026-11-11
- **Status:** Approved
- **Area:** Workflow / Data Management
- **Context:** The team needed to define how members collaborate during EDA, preprocessing and model development, and whether the Kaggle dataset files can be kept in the repository.
- **Decision:**
  1. **Git workflow:** each member works on their own branch. Changes reach `main` exclusively through Pull Requests reviewed by another team member. No direct commits to `main`.
  2. **EDA:** each member explores independently. The EDA lead owns `01_eda.ipynb` and integrates relevant findings into the final notebook.
  3. **Notebooks:** each notebook has one designated owner. No simultaneous editing by multiple members.
  4. **Preprocessing and data split:** implemented in a shared Python Pipeline under `src/`, ensuring consistent processing across models.
  5. **Model experiments:** each member maintains their own model notebook, imports the shared Pipeline and records metrics in `results/` using a common format.
  6. **Dataset:** retain `Train.csv` and `Test.csv` in the repository. The Kaggle dataset is licensed under CC0, allowing redistribution. No changes to `.gitignore` are required.
- **Dataset license note:** the CC0 license of the Kaggle dataset was confirmed by human review on Kaggle.
- **Documentation:** add the Kaggle dataset source and Analytics Vidhya reference to the README.
- **Approval:** Approved by a human team member, 2026-11-11.
- **Consequences:** The team follows a branch + Pull Request workflow with single-owner notebooks and a shared preprocessing Pipeline. `Train.csv` and `Test.csv` remain versioned in the repository under the confirmed CC0 license, with no `.gitignore` changes.

---

<!-- Add new decisions below using the same structure. Preserve previous records. -->
