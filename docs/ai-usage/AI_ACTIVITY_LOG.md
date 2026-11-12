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

---

<!-- Add new activities below using the same structure. Preserve previous records. -->
