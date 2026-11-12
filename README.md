# customer-segmentation-multiclass

Customer segmentation through multiclass classification using demographic and behavioral customer data to predict customer segments (classes A, B, C and D).

## Dataset

- **Source (Kaggle):** [Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)
- **Complementary reference:** [Analytics Vidhya – JanataHack: Customer Segmentation](https://datahack.analyticsvidhya.com/contest/janatahack-customer-segmentation/) (the original hackathon whose data this Kaggle dataset reproduces)
- **License:** CC0 (confirmed on Kaggle), which allows redistribution of the dataset in this repository.

## Files

- `Train.csv` — the only data source: split once into train / validation / test (70/15/15), stratified by `Segmentation` (`random_state=42`).
- `Test.csv` — **not used.** Most of its IDs (2,332 of 2,627) also appear in `Train.csv` with different values and labels, so it is not an independent test set (see D-006 in the [Decision Log](docs/ai-usage/DECISION_LOG.md)).
- Target variable: `Segmentation` (multiclass; classes A, B, C and D).
