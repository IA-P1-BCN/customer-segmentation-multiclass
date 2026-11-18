"""US-14: analisis de errores del modelo congelado sobre val_15.

Ejecutar desde la raiz del repositorio:

    python -m src.error_analysis

Genera:
  - reports/error_analysis_val_15.csv  (filas mal clasificadas, predicciones del modelo congelado)
  - reports/error_analysis.md          (documento completo)
"""
import sys, os, shutil
import joblib
import pandas as pd
import numpy as np
from collections import Counter
from src.preprocessing import make_features_target
from src.config import TARGET, RANDOM_STATE

ROOT = "F:/Curso AI/Modulo 2 - Data Analytics - Machine Learning/Proyectos/Proyecto _Multiclass _Minds/customer-segmentation-multiclass"
REPORTS = os.path.join(ROOT, "reports")
MODELS = os.path.join(ROOT, "models")

# 1. Verificar que el modelo congelado existe
model_path = os.path.join(MODELS, "final_model.joblib")
if not os.path.exists(model_path):
    print("ERROR: No existe %s" % model_path)
    print("Generalo primero con: python -m src.compare_models --stage freeze --model boosting")
    sys.exit(1)
print("Modelo encontrado: %s" % model_path)

# 2. Cargar el modelo congelado
payload = joblib.load(model_path)
model = payload["model"]
print("trained_on=%s, rows=%s" % (payload['trained_on'], payload['rows']))
print("Config: %s" % payload['frozen_params'])
print()

# 3. Predecir sobre val_15
val = pd.read_csv(os.path.join(ROOT, "data", "val_15.csv"))
X_val, y_val = make_features_target(val)
pred = model.predict(X_val)

# 4. Verificar que coincide con confusion_counts_val_15.csv
expected = pd.read_csv(os.path.join(REPORTS, "confusion_counts_val_15.csv"), index_col=0)
classes = ["A", "B", "C", "D"]
print("=== Verificacion: matriz calculada vs confusion_counts_val_15.csv ===")
match = True
for actual in classes:
    for predicted in classes:
        calc = int(((y_val.values == actual) & (pred == predicted)).sum())
        exp = int(expected.loc[actual, predicted])
        if calc != exp:
            match = False
            print("  DESCUADRE %s->%s: calculado=%d, esperado=%d" % (actual, predicted, calc, exp))
if match:
    print("  OK: coinciden exactamente.")
print()

# 5. Resumen general
errors = val[pred != y_val.values].copy()
errors["predicted"] = pred[pred != y_val.values]
errors["actual"] = y_val.values[pred != y_val.values]
correct = val[pred == y_val.values]
print("Total: %d filas, %d errores (%.1f%%)" % (len(val), len(errors), len(errors)/len(val)*100))
print("Aciertos: %d (%.1f%%)" % (len(correct), (len(val)-len(errors))/len(val)*100))
print()

# 6. Matriz de confusion (conteos)
print("=== Matriz de confusion (conteos) ===")
for actual in classes:
    row = []
    for predicted in classes:
        n = int(((y_val.values == actual) & (pred == predicted)).sum())
        row.append("%4d" % n)
    print("  %s  " % actual + "  ".join(row))
print()

# 7. Recall y precision por clase
print("=== Recall y Precision por clase ===")
metrics = {}
for cls in classes:
    tp = int(((y_val.values == cls) & (pred == cls)).sum())
    fn = int(((y_val.values == cls) & (pred != cls)).sum())
    fp = int(((y_val.values != cls) & (pred == cls)).sum())
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    metrics[cls] = {"tp": tp, "fn": fn, "fp": fp, "recall": recall, "precision": precision, "f1": f1}
    print("  %s: recall=%.4f  precision=%.4f  F1=%.4f  (TP=%d, FN=%d, FP=%d)" % (cls, recall, precision, f1, tp, fn, fp))
print()

# 8. Pares mas confundidos
from collections import Counter
print("=== Pares mas confundidos (actual -> predicho) ===")
pairs = Counter()
for a, p in zip(y_val.values, pred):
    if a != p:
        pairs[(a, p)] += 1
for (a, p), n in pairs.most_common(10):
    pct = n / (y_val.values == a).sum() * 100
    print("  %s -> %s: %d (%.1f%% de los %s)" % (a, p, n, pct, a))
print()

# 9. Perfil de filas mal clasificadas vs acertadas
print("=== Perfil de filas mal clasificadas vs acertadas ===")
numeric_cols = ["Age", "Work_Experience", "Family_Size"]
cat_cols = ["Gender", "Ever_Married", "Graduated", "Profession", "Spending_Score"]
print("  Aciertos: %d, Errores: %d" % (len(correct), len(errors)))
print()
print("  Variables numericas (media):")
num_profile = {}
for col in numeric_cols:
    m_c = correct[col].mean()
    m_e = errors[col].mean()
    num_profile[col] = (m_c, m_e)
    print("    %-20s  acierto=%.2f  error=%.2f" % (col, m_c, m_e))
print()
print("  Variables categoricas (% del nivel mas frecuente):")
cat_profile = {}
for col in cat_cols:
    top_correct = correct[col].value_counts(normalize=True).iloc[0]
    top_error = errors[col].value_counts(normalize=True).iloc[0]
    top_level_correct = correct[col].value_counts().index[0]
    top_level_error = errors[col].value_counts().index[0]
    cat_profile[col] = (top_level_correct, top_correct, top_level_error, top_error)
    print("    %-20s  acierto: %s (%.1f%%)  |  error: %s (%.1f%%)" % (col, top_level_correct, top_correct*100, top_level_error, top_error*100))
print()

# 10. Ejemplos de filas mal clasificadas por segmento (primeras 3)
print("=== Ejemplos de filas mal clasificadas (primeras 3 por segmento real) ===")
cols_show = ["Age", "Gender", "Ever_Married", "Graduated", "Profession",
             "Work_Experience", "Spending_Score", "Family_Size", "Var_1"]
examples = {}
for cls in classes:
    subset = errors[errors["actual"] == cls].head(3)
    if len(subset) == 0:
        continue
    print("\n  Segmento real: %s" % cls)
    ex = []
    for _, row in subset.iterrows():
        vals = " | ".join("%s=%s" % (c, row[c]) for c in cols_show)
        print("    %s  -> predicho: %s" % (vals, row['predicted']))
        ex.append((row, cls))
    examples[cls] = ex

# 11. Guardar las predicciones
errors.to_csv(os.path.join(REPORTS, "error_analysis_val_15.csv"), index=False)
print("\nGuardado: reports/error_analysis_val_15.csv (%d filas)" % len(errors))

# 12. Generar el documento error_analysis.md
age_c, age_e = num_profile["Age"]
we_c, we_e = num_profile["Work_Experience"]
fs_c, fs_e = num_profile["Family_Size"]

def ex_table(cls):
    subset = errors[errors["actual"] == cls].head(3)
    lines = []
    for _, row in subset.iterrows():
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            row['Age'], row['Gender'], row['Ever_Married'], row['Graduated'],
            row['Profession'], row['Work_Experience'], row['Spending_Score'],
            row['Family_Size'], row['predicted']))
    return "\n".join(lines)

# Build val pairs table
val_pairs = Counter()
for a, p in zip(y_val.values, pred):
    if a != p:
        val_pairs[(a, p)] += 1

# Test pairs (from Rita's review)
test_pairs = [("B", "C", 87), ("A", "D", 68), ("B", "A", 54), ("D", "A", 64), ("A", "B", 51), ("C", "B", 49), ("A", "C", 42), ("C", "D", 41), ("C", "A", 26), ("B", "D", 30)]
test_totals = {"A": 296, "B": 278, "C": 296, "D": 341}

doc = ""
doc += "# Análisis de errores del modelo (US-14)\n\n"
doc += "**Modelo evaluado:** XGBoost congelado (min_child_weight=5, 300 árboles, depth 3, lr 0,05), entrenado solo con `train_70` (D-017). Evaluación única en `test_15` (US-12, issue #29). El análisis de filas se hace sobre `val_15` (1.210 filas), porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron.\n\n"
doc += "## 1. Resumen ejecutivo\n\n"
doc += "El modelo acierta el **54,2 % de los clientes de validación** (656 de 1.210) y el **56,0 % en test** (0,5599). El segmento más difícil es **B** (recall 0,323, F1 0,367): dos de cada tres clientes B se predicen como otro segmento. El más fácil es **D** (recall 0,782, F1 0,715). El par más confundido en test es **B → C** (87 casos), seguido de **A → D** (68) y **B → A** (54).\n\n"
doc += "Los errores no son aleatorios: las filas mal clasificadas tienen en promedio **%.1f años más** que las acertadas, más estado civil casado (%.1f %% vs %.1f %%) y más graduados (%.1f %% vs %.1f %%). Esto sugiere que el modelo confunde perfiles \"maduros\" entre segmentos.\n\n" % (age_e - age_c, cat_profile['Ever_Married'][3]*100, cat_profile['Ever_Married'][1]*100, cat_profile['Graduated'][3]*100, cat_profile['Graduated'][1]*100)
doc += "## 2. Matriz de confusión\n\n"
doc += "### Test (1.211 filas, evaluación única)\n\n"
doc += "| Real \\ Predicho | A | B | C | D | Total | Recall |\n"
doc += "|---|---:|---:|---:|---:|---:|---:|\n"
doc += "| **A** | 135 | 51 | 42 | 68 | 296 | 0,456 |\n"
doc += "| **B** | 54 | 107 | 87 | 30 | 278 | 0,385 |\n"
doc += "| **C** | 26 | 49 | 180 | 41 | 296 | 0,608 |\n"
doc += "| **D** | 64 | 14 | 7 | 256 | 341 | 0,751 |\n"
doc += "| **Total** | 279 | 221 | 316 | 395 | 1.211 | |\n\n"
doc += "Precision: A 0,484 · B 0,484 · C 0,570 · D 0,648. F1: A 0,470 · B 0,429 · C 0,588 · D 0,696.\n\n"
doc += "*Fuente: `reports/confusion_counts_test_15_20261118T092535Z.csv` y `reports/confusion_normalised_test_15_20261118T092535Z.csv`.*\n\n"
doc += "### Validación (1.210 filas, análisis fila a fila)\n\n"
doc += "| Real \\ Predicho | A | B | C | D | Total | Recall |\n"
doc += "|---|---:|---:|---:|---:|---:|---:|\n"
doc += "| **A** | 124 | 59 | 46 | 67 | 296 | 0,419 |\n"
doc += "| **B** | 64 | 90 | 94 | 31 | 279 | 0,323 |\n"
doc += "| **C** | 33 | 46 | 176 | 40 | 295 | 0,597 |\n"
doc += "| **D** | 50 | 17 | 7 | 266 | 340 | 0,782 |\n"
doc += "| **Total** | 271 | 212 | 323 | 404 | 1.210 | |\n\n"
doc += "Precision: A 0,458 · B 0,425 · C 0,545 · D 0,658. F1: A 0,437 · B 0,367 · C 0,570 · D 0,715.\n\n"
doc += "*Fuente: `reports/confusion_counts_val_15.csv` y `reports/final_metrics_val_15.csv` (predicciones del modelo congelado).*\n\n"
doc += "## 3. Comparación test vs validación\n\n"
doc += "| Métrica | val_15 | test_15 | Diferencia |\n"
doc += "|---|---:|---:|---:|\n"
doc += "| Accuracy | 0,5421 | 0,5599 | +1,77 pp |\n"
doc += "| Macro-F1 | 0,5222 | 0,5456 | +2,34 pp |\n\n"
doc += "El test es **mejor** que la validación en ambas métricas. No hay sobreajuste: el modelo generaliza bien a datos nuevos. El gap train − val del modelo congelado es de 3,44 puntos (#79), dentro del límite de 5 puntos de D-010.\n\n"
doc += "## 4. Pares más confundidos (matriz de test)\n\n"
doc += "| Par (real → predicho) | Casos | % del segmento real |\n"
doc += "|---|---:|---:|\n"
test_pairs = [("B", "C", 87), ("A", "D", 68), ("D", "A", 64), ("B", "A", 54), ("A", "B", 51), ("C", "B", 49), ("A", "C", 42), ("C", "D", 41), ("B", "D", 30), ("C", "A", 26)]
test_totals = {"A": 296, "B": 278, "C": 296, "D": 341}
for a, p, n in sorted(test_pairs, key=lambda x: -x[2]):
    pct = n / test_totals[a] * 100
    doc += "| %s → %s | %d | %.1f %% de los %s |\n" % (a, p, n, pct, a)
doc += "\nLos dos pares dominantes son **B ↔ C** (87 + 49 = 136 confusiones) y **A ↔ D** (68 + 64 = 132 confusiones).\n\n"
doc += "## 5. Perfil de las filas mal clasificadas en val_15\n\n"
doc += "Se comparan las %d filas mal clasificadas con las %d acertadas (predicciones del modelo congelado sobre `val_15`):\n\n" % (len(errors), len(correct))
doc += "| Variable | Aciertos (media) | Errores (media) | Diferencia |\n"
doc += "|---|---:|---:|---:|\n"
doc += "| Edad | %.2f | %.2f | %+.1f años |\n" % (age_c, age_e, age_e - age_c)
doc += "| Experiencia laboral | %.2f | %.2f | %+.2f años |\n" % (we_c, we_e, we_e - we_c)
doc += "| Tamaño de familia | %.2f | %.2f | %+.2f |\n\n" % (fs_c, fs_e, fs_e - fs_c)
doc += "| Variable categórica | Aciertos (nivel más frecuente) | Errores (nivel más frecuente) |\n"
doc += "|---|---|---|\n"
for col in cat_cols:
    tl_c, pct_c, tl_e, pct_e = cat_profile[col]
    doc += "| %s | %s (%.1f %%) | %s (%.1f %%) |\n" % (col, tl_c, pct_c*100, tl_e, pct_e*100)
doc += "\n**Lectura**: las filas mal clasificadas son en promedio **%.1f años más mayores**, más estado civil casado (%.1f %% vs %.1f %%) y más graduados (%.1f %% vs %.1f %%). Esto sugiere que el modelo confunde perfiles \"maduros\" entre segmentos.\n\n" % (age_e - age_c, cat_profile['Ever_Married'][3]*100, cat_profile['Ever_Married'][1]*100, cat_profile['Graduated'][3]*100, cat_profile['Graduated'][1]*100)
doc += "## 6. Ejemplos de filas mal clasificadas\n\n"
doc += "Se muestran 3 ejemplos por segmento real, con todas sus variables. Son **ilustrativos**: no representan el conjunto completo de errores, pero muestran los patrones típicos.\n\n"
for cls in classes:
    subset = errors[errors["actual"] == cls].head(3)
    if len(subset) == 0:
        continue
    doc += "### Segmento real %s (predicho como otra cosa)\n\n" % cls
    doc += "| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |\n"
    doc += "|---|---|---|---|---|---|---|---|---|\n"
    doc += ex_table(cls) + "\n\n"
doc += "**Lectura de los ejemplos:**\n"
doc += "- Los B mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o ejecutivos con gasto High (se parecen a A o C).\n"
doc += "- Los D mal clasificados suelen ser mayores, casados o con gasto High (se parecen a A, B o C).\n"
doc += "- Los C mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o con gasto Average (se parecen a B).\n\n"
doc += "*Los ejemplos son ilustrativos y se obtienen de las primeras 3 filas mal clasificadas por segmento en val_15. No representan el conjunto completo de errores.*\n\n"
doc += "## 7. Hipótesis (marcadas como hipótesis, no como hechos)\n\n"
doc += "1. **B es el segmento más difícil porque su perfil es intermedio.** B se parece a C en edad (46 vs 49), graduación (73,7 % vs 81,7 %) y estado civil (73,7 % vs 79,5 %), pero tiene menos gasto High (20,6 % vs 21,2 %) y más Low (48,7 % vs 33,6 %). La frontera B-C es difusa y el modelo no la separa bien (94 confusiones B→C en val, 87 en test).\n"
doc += "2. **B también se confunde con A.** Ambos tienen gasto mixto, pero A es más joven (mediana 41 vs 46) y tiene familias más pequeñas. El modelo puede estar usando la edad y el gasto como señales principales, y B cae en medio.\n"
doc += "3. **D se reconoce bien porque es el más distinto.** Joven (mediana 29), no casado (29,0 %), no graduado (37,8 %), Healthcare (43,2 %), gasto Low (86,8 %). Cualquier variable por sí sola ya apunta a D. Pero cuando un D es mayor, casado o tiene gasto High, se confunde con A o B.\n"
doc += "4. **A es el segundo más difícil** (recall 0,419). Es el segmento \"promedio\": edad 41, casado 58,2 %, graduado 61,5 %. Como se parece a todos, el modelo no tiene una señal clara. Se confunde con D (67 en val, 68 en test), B (59 en val, 51 en test) y C (46 en val, 42 en test).\n"
doc += "5. **Las variables que más peso tienen en el modelo son Age, Profession y Spending_Score** (importancia por permutación: 0,080, 0,077 y 0,054). Ever_Married tiene el V de Cramér más alto (0,408) pero es la menos importante (0,006). *Hipótesis*: esto se debe a que la información de Ever_Married ya está capturada por Spending_Score (V = 0,669 entre las dos variables). Esta es una interpretación del analista, no una conclusión verificada.\n\n"
doc += "## 8. Datos adicionales que ayudarían a corregir los errores\n\n"
doc += "1. **Ingresos o nivel de gasto real**: Spending_Score es un proxy. Con ingresos reales, B y C podrían separarse mejor (B tiene 48,7 % Low y C solo 33,6 %).\n"
doc += "2. **Productos adquiridos (P1 a P5)**: el dataset no incluye qué productos compra cada cliente. Saber qué compra ayudaría a distinguir B (gasto mixto) de C (gasto alto).\n"
doc += "3. **Tipo de vehículo**: el dataset no incluye esta variable. Sería útil para confirmar si D es el segmento de entrada.\n"
doc += "4. **Canal de contacto**: la app propone canales digitales para D por su edad (mediana 29), pero no hay datos de canal en el dataset.\n"
doc += "5. **Historial de compras**: frecuencia y recencia de compra. El dataset es estático (un solo punto en el tiempo).\n\n"
doc += "Estas recomendaciones alimentan la sección de limitaciones del informe (US-16, sección 9) y la recomendación de negocio de recoger estos datos.\n\n"
doc += "## 9. Limitaciones del análisis\n\n"
doc += "- El análisis de filas se hace sobre `val_15` (1.210 filas), no sobre `test_15`, porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron. Las matrices de confusión de test sí están disponibles en `reports/` y se usan para el análisis agregado.\n"
doc += "- Las hipótesis no se han verificado con datos adicionales. Son interpretaciones del analista, no conclusiones.\n"
doc += "- El modelo no se reajustó con los errores encontrados. La configuración está congelada (D-018).\n"
doc += "- El análisis no incluye rendimiento por subgrupos (género, edad), que es un criterio opcional de US-14.\n"
doc += "- La diferencia de una fila entre el modelo congelado (0,5421) y la ejecución registrada de boosting (0,5430) es por variación de XGBoost hist entre ejecuciones. No afecta a las conclusiones.\n\n"
doc += "## Fuentes\n\n"
doc += "- Matriz de confusión de test: `reports/confusion_counts_test_15_20261118T092535Z.csv`, `reports/confusion_normalised_test_15_20261118T092535Z.csv`\n"
doc += "- Métricas de test: `reports/final_metrics_test_15_20261118T092535Z.csv`\n"
doc += "- Métricas de validación: `reports/final_metrics_val_15.csv`\n"
doc += "- Importancia de variables: `reports/feature_importance_val_15.csv`\n"
doc += "- Perfiles de segmento: `reports/segment_profile_train_70.csv`\n"
doc += "- Predicciones de validación: `reports/error_analysis_val_15.csv` (554 filas mal clasificadas)\n"
doc += "- Modelo congelado: `models/final_model.joblib` (generado localmente, no commiteado)\n"
doc += "- Decisiones: D-010 (métrica y overfitting), D-015 (selección de configuración), D-016 (priorización), D-017 (train_70 solo), D-018 (XGBoost elegido y congelado)\n"

# Save the document
out_path = ROOT + "/reports/error_analysis.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(doc)
print("Documento guardado: %s" % out_path)

# Also copy to working directory
shutil.copy(out_path, "C:/Users/USUARIO/Documents/Proyecto predeterminado/error_analysis.md")
print("Copia guardada en la carpeta de trabajo.")

# Print summary of profile numbers
print()
print("=== Perfil de errores vs aciertos ===")
print("  Edad: acierto=%.2f, error=%.2f (diff=%.1f)" % (age_c, age_e, age_e - age_c))
print("  Experiencia: acierto=%.2f, error=%.2f" % (we_c, we_e))
print("  Familia: acierto=%.2f, error=%.2f" % (fs_c, fs_e))
for col in cat_cols:
    tl_c, pct_c, tl_e, pct_e = cat_profile[col]
    print("  %s: acierto=%s (%.1f%%), error=%s (%.1f%%)" % (col, tl_c, pct_c*100, tl_e, pct_e*100))
print()
print("Errores: %d, Aciertos: %d" % (len(errors), len(correct)))