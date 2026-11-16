# Segment profiles, prioritisation and influential variables (US-13)

This document answers three business questions with the project data:

- **N1.** Who is each segment?
- **N2.** Which segment should be prioritised?
- **N3.** Which variables matter most for belonging to a segment?

The technical report (US-16) and the business presentation (US-17) cite the figures from here.

**Status: draft.** Three parts are pending and are marked in the text:

| Part | Status |
|---|---|
| Profile per segment (section 2) | Computed from a recorded run |
| Prioritisation rule (section 3) | Proposed, pending team approval |
| Feature importance from the model (section 4) | Pending US-12 |
| Campaign table (section 5) | Draft, pending team approval |

## 1. Where the figures come from

Every figure in sections 2 and 3 comes from `src/segment_profile.py`, which reads only `data/train_70.csv` (5,647 customers). `val_15` and `test_15` are not used.

```
python -m src.segment_profile
```

| Item | Value |
|---|---|
| Recorded run | 2026-11-16 14:31 UTC |
| Environment | Python 3.12.10, pandas 3.1.1 |
| Partition | `data/train_70.csv`, 5,647 rows, SHA-256 checked against D-013 |
| Summary table | `reports/segment_profile_train_70.csv` |
| Detailed table | `reports/segment_distributions_train_70.csv` |

Three notes for reading the tables:

- **Percentages are computed over the customers who have a value.** A customer with no marital status counts neither as married nor as not married. This is why some figures differ by about one point from the notebook `02_eda_train70_gasto_estado_civil.ipynb`, which shows missing values as one more category (for example, married customers in A: 58.2 % here and 57.2 % there).
- **`Spending_Score` is a proxy of customer value.** The dataset has no income and no purchase amounts.
- **The figures describe the customers; they do not explain causes.** A segment having more married customers does not mean that getting married leads to that segment.

## 2. Profile of each segment (N1)

| | A | B | C | D | All |
|---|---:|---:|---:|---:|---:|
| Customers | 1,380 | 1,301 | 1,379 | 1,587 | 5,647 |
| % of train | 24.4 | 23.0 | 24.4 | 28.1 | 100 |
| Age, median (years) | 41 | 46 | 49 | 29 | 41 |
| Age, mean (years) | 44.7 | 48.2 | 49.6 | 33.9 | 43.7 |
| Work experience, median (years) | 1 | 1 | 1 | 1 | 1 |
| Work experience, mean (years) | 2.89 | 2.40 | 2.25 | 3.03 | 2.66 |
| Family size, median | 2 | 2 | 3 | 3 | 3 |
| Family size, mean | 2.49 | 2.68 | 2.95 | 3.21 | 2.84 |
| % male | 53.7 | 53.3 | 52.4 | 56.9 | 54.2 |
| % ever married | 58.2 | 73.7 | 79.5 | 29.0 | 58.8 |
| % graduated | 61.5 | 72.9 | 81.7 | 37.8 | 62.4 |
| Most frequent profession | Artist | Artist | Artist | Healthcare | Artist |
| % in that profession | 28.4 | 41.1 | 53.8 | 43.2 | 31.4 |
| % Low spending | 69.1 | 48.7 | 33.6 | 86.8 | 60.7 |
| % Average spending | 17.2 | 30.7 | 45.2 | 6.6 | 24.2 |
| % High spending | 13.7 | 20.6 | 21.2 | 6.6 | 15.1 |

The three most frequent professions in each segment:

| Segment | 1st | 2nd | 3rd |
|---|---|---|---|
| A | Artist (28.4 %) | Entertainment (19.7 %) | Engineer (13.5 %) |
| B | Artist (41.1 %) | Entertainment (10.8 %) | Executive (10.8 %) |
| C | Artist (53.8 %) | Executive (8.9 %) | Healthcare (7.8 %) |
| D | Healthcare (43.2 %) | Entertainment (10.5 %) | Doctor (9.1 %) |

EDA figures that go with this table: [spending by segment](figures/eda_spending_by_segment.png) and [marital status by segment](figures/eda_married_by_segment.png).

### Description in words

The names in quotes are **team hypotheses**, used to talk about the segments. The dataset only calls them A, B, C and D and does not explain what they mean.

- **D, "young low spenders".** It is the largest segment (28.1 %) and the most different from the other three. Its customers are the youngest (median age 29), most have never married (29.0 % married) and have not graduated (37.8 % graduated), they work mainly in Healthcare (43.2 %) and 86.8 % have Low spending.
- **C, "mature graduates with the highest spending".** Its customers are the oldest (median age 49), the most often married (79.5 %) and the most often graduated (81.7 %). More than half are Artists (53.8 %). It is the segment with the least Low spending (33.6 %) and the most Average (45.2 %) and High (21.2 %) spending.
- **B, "married graduates with medium spending".** It resembles C with somewhat lower values throughout: median age 46, 73.7 % married, 72.9 % graduated and 41.1 % Artists. Its High spending (20.6 %) is almost that of C, but it has more Low spending (48.7 %).
- **A, "mixed profile".** Its values are close to those of all customers in age (41), married (58.2 %) and graduated (61.5 %). It has the most evenly spread professions and the smallest families (mean 2.49). In spending it is closer to D: 69.1 % Low.

Two variables hardly distinguish the segments: gender (between 52.4 % and 56.9 % male) and work experience (median of 1 year in all four).

B and C are very similar. The model can be expected to have trouble separating them; the error analysis in US-14 will confirm this or not.

## 3. Segment to prioritise (N2)

> **Status: proposed, pending team approval.** The team also has to confirm what "on the train split" means in the user story; here it is read as "computed with the 5,647 customers of `train_70`".

**Proposed rule:** prioritise the segment with the most High-spending customers.

The reason is that the story asks for two criteria, the size of the segment and its share of High spending, and the number of High-spending customers is the product of the two. A large segment that spends little does not come first, and neither does a small one that spends a lot.

| Segment | Customers | % High spending | High-spending customers | % of all High |
|---|---:|---:|---:|---:|
| **C** | 1,379 | 21.2 | **292** | 34.2 |
| B | 1,301 | 20.6 | 268 | 31.4 |
| A | 1,380 | 13.7 | 189 | 22.1 |
| D | 1,587 | 6.6 | 105 | 12.3 |
| All | 5,647 | 15.1 | 854 | 100 |

**Result with this rule: C**, with 292 High-spending customers, 34.2 % of all of them. B is close behind (268). Together they hold 65.6 % of the High-spending customers.

The result depends on the rule, which is why the team has to approve it:

| Rule | Segment selected | Comment |
|---|---|---|
| Most High-spending customers (proposed) | C (292) | Combines size and spending |
| Highest % of High spending | C (21.2 %) | Almost tied with B (20.6 %); ignores size |
| Size only | D (28.1 %) | It is the segment that spends the least (6.6 % High) |

Limits of this answer:

- Prioritising by `Spending_Score` is prioritising by a proxy. Without income or purchase amounts, the value of each segment cannot be calculated.
- The rule does not say what to do with D, the largest segment. Its low spending today does not rule out that it is interesting for its volume or its potential; these data cannot measure that.

## 4. Most influential variables (N3)

This section combines two sources. The second one does not exist yet.

### 4.1. What the EDA says

Source: `02_eda_train70_gasto_estado_civil.ipynb`, section 8, on `train_70`. Cramér's V measures how much one variable helps to guess another: 0 is not at all and 1 is completely.

| Variable | Cramér's V with the segment | Reading |
|---|---:|---|
| `Ever_Married` | 0.408 | The one that best separates D (29.0 % married) from the rest |
| `Spending_Score` | 0.302 | Separates D (86.8 % Low) from B and C |

The table in section 2 adds three descriptive hints, with no strength measure computed in a merged notebook:

- **Age:** D has a median of 29 years and the other three between 41 and 49.
- **Graduation:** it ranges from 37.8 % in D to 81.7 % in C.
- **Profession:** Healthcare dominates in D and Artist in C.

Three clarifications:

- **No single variable is enough.** The associations are moderate. The segment comes from combining several variables.
- **Marital status and spending overlap.** Every customer in `train_70` who has never married has Low spending (V = 0.669 between the two variables). Part of what one contributes is already contributed by the other.
- **`Spending_Score` and `Profession` are proxies.** They stand in for income level, which is not in the dataset. Executive (65.4 % High) and Lawyer (51.6 % High) are the only professions where High spending is the majority.

The EDA on outliers and data leakage (PR #64) measures the strength of the numeric variables, including age. Its figures will be added here once it is merged into `develop`.

### 4.2. What the model says

> **Pending US-12.** The feature importance of the frozen model will be added when it exists. Until then this section makes no claim about the model.

Two warnings must be kept when it is added: importance is not causality, and two overlapping variables (such as marital status and spending) share the importance between them.

## 5. Proposed campaign per segment

> **Status: draft, pending team approval.** The campaigns are **business hypotheses**, not model results. The dataset contains no campaigns, products, vehicle type or income.

The short text is what the app would show (US-15).

| Segment | Text for the app | Profile trait it is based on |
|---|---|---|
| A | General offer with options for small households. | Profile close to the average; smallest families (mean 2.49); 69.1 % Low spending |
| B | Mid-range offer for families. | 73.7 % married; spending split between Low (48.7 %) and Average (30.7 %) |
| C | Mid-range and high-end offer with preferential service. | Prioritised segment (section 3); 45.2 % Average and 21.2 % High; median age 49 |
| D | Entry-level offer at an affordable price, through digital channels. | The youngest (median age 29); 86.8 % Low spending |

The digital channel for D is an assumption based on age; the dataset has no channel data.

## 6. Limitations

- There is no income, product (P1 to P5) or vehicle type. The strategy cannot be adapted to them with these data; the recommendation is to collect them.
- Segments A to D have no explicit meaning in the dataset. The names in section 2 are hypotheses.
- Everything is computed on `train_70`. These are descriptions of that sample of 5,647 customers.
- Per D-009, there are customers with identical profiles in different segments. The profiles describe group tendencies and cannot classify an individual customer with certainty.

## 7. Pending

- [ ] The team approves the prioritisation rule and confirms what "on the train split" means (section 3).
- [ ] Add the feature importance from US-12 (section 4.2).
- [ ] Add the figures from the numeric EDA once PR #64 is in `develop` (section 4.1).
- [ ] The team approves the campaign table and Isbel integrates it into the app (section 5).
