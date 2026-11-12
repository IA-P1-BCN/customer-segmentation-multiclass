# customer-segmentation-multiclass

Customer segmentation through multiclass classification using demographic and behavioral customer data to predict customer segments (classes A, B, C and D).

## Dataset

- **Source (Kaggle):** [Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)
- **Complementary reference:** [Analytics Vidhya – JanataHack: Customer Segmentation](https://datahack.analyticsvidhya.com/contest/janatahack-customer-segmentation/) (the original hackathon whose data this Kaggle dataset reproduces)
- **License:** CC0 (confirmed on Kaggle), which allows redistribution of the dataset in this repository.

## Files

- `Train.csv` — labeled data for EDA, preprocessing, model development and validation.
- `Test.csv` — separate test data for final predictions.
- Target variable: `Segmentation` (multiclass; classes A, B, C and D).

## Git Collaboration Workflow

The project uses an integration branch: `feature/* → develop → main`.

- **`main`** — stable branch. Only receives integrated, tested and approved versions; no direct commits.
- **`develop`** — integration branch. Receives finished features and enables joint testing before preparing a release; no direct commits.
- **Task branches** (`feature/*`, `fix/*`, `docs/*`, `refactor/*`) — individual branches created from `develop`, where each member develops their task.

Pull Requests:

- All task branches open small, specific PRs exclusively into `develop`, reviewed by another team member the same day.
- All task-branch PRs are integrated into `develop` using **Squash Merge**.
- When a milestone is validated, a PR is opened from `develop` into `main`, using a **normal Merge Commit** (not Squash Merge or Rebase).

`main` and `develop` must require Pull Requests and at least one approval. If the repository plan or configuration does not allow these protections, the rules remain mandatory by team agreement as documented in `AGENTS.md`; plan limitations must be checked manually.
