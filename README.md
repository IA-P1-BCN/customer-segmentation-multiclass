# Customer Segmentation — Multiclass Minds

Clasificación multiclase de clientes en segmentos A, B, C y D a partir de datos demográficos y de comportamiento. Proyecto M2 (Data Analytics & Machine Learning), nivel Esencial, entrega 18/11/2026.

## Equipo
Rita, Isbel, Pedro y Brian.

## Dataset
- **Fuente:** [Kaggle – Customer Segmentation](https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation)
- **Referencia complementaria:** [Analytics Vidhya – JanataHack: Customer Segmentation](https://datahack.analyticsvidhya.com/contest/janatahack-customer-segmentation/)
- **Licencia:** CC0 (confirmada en Kaggle), que permite redistribución del dataset en este repositorio.
- `Train.csv` es la única fuente de datos. Se divide una sola vez en `train_70.csv`, `val_15.csv` y `test_15.csv` (70/15/15, estratificado por `Segmentation`, `random_state=42`).
- El `Test.csv` original de Kaggle **no forma parte del dataset/repositorio** (D-012). El conjunto de prueba del proyecto es `test_15.csv`.
- Variable objetivo: `Segmentation` (multiclase; clases A, B, C, D).

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Entorno de referencia: Python 3.12.3 (ver A-009 / A-012).

## Reproducibilidad
- Semilla global: `RANDOM_STATE = 42` en `src/config.py`. Importarla siempre, nunca hardcodear.
- Split: `python src/split_data.py` genera `data/train_70.csv`, `data/val_15.csv` y `data/test_15.csv`.
- Métrica principal: macro-F1 en validación; accuracy también se reporta. Overfitting: diferencia absoluta en accuracy < 5 puntos entre train y validation (D-010).

## Estructura del repositorio
```
data/            # Train.csv + splits (train_70, val_15, test_15)
src/             # split_data.py, config.py, data_quality.py, (Pipeline US-05)
results/         # métricas por modelo (convención en results/README.md)
reports/         # figuras y tablas del EDA (nulos, etc.)
docs/ai-usage/   # DECISION_LOG.md, AI_ACTIVITY_LOG.md
01_eda_inicial.ipynb
requirements.txt
AGENTS.md
```

## Cómo ejecutar
- **EDA:** abrir `01_eda_inicial.ipynb` (Jupyter/VS Code) y ejecutar "Restart & Run All".
- **Modelos:** notebooks/scripts en `feature/model-*` (regresión logística, random forest, boosting, SVM) importando el Pipeline común de `src/`.
- **App:** *(pendiente — US-15)* `streamlit run app.py`
- **Informe técnico:** *(pendiente — US-16)* ver `reports/` y el informe.

## Resultados principales
- Baseline (clase mayoritaria, D): accuracy ≈ 28,1 %, macro-F1 ≈ 0,11 (D-010).
- *(Pendiente — US-11)* Mejor modelo congelado, métricas en test y feature importance.

## Tablero
- GitHub Project #58: https://github.com/orgs/IA-P1-BCN/projects/58

## Decisiones y trazabilidad
- [Decision Log](docs/ai-usage/DECISION_LOG.md) — D-001 a D-013.
- [AI Activity Log](docs/ai-usage/AI_ACTIVITY_LOG.md) — A-001 a A-012.
- Flujo Git: `feature/* → develop → main`, con Squash Merge a `develop`.

## Licencia
Dataset bajo CC0. Código del proyecto: por definir por el equipo.
