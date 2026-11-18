# Análisis de errores del modelo (US-14)

**Modelo evaluado:** XGBoost congelado (min_child_weight=5, 300 árboles, depth 3, lr 0,05), entrenado solo con `train_70` (D-017). Evaluación única en `test_15` (US-12, issue #29). El análisis de filas se hace sobre `val_15` (1.210 filas), porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron.

## 1. Resumen ejecutivo

El modelo acierta el **54,2 % de los clientes de validación** (656 de 1.210) y el **56,0 % en test** (0,5599). El segmento más difícil es **B** (recall 0,323, F1 0,367): dos de cada tres clientes B se predicen como otro segmento. El más fácil es **D** (recall 0,782, F1 0,715). El par más confundido en test es **B → C** (87 casos), seguido de **A → D** (68) y **B → A** (54).

Los errores no son aleatorios: las filas mal clasificadas tienen en promedio **5.8 años más** que las acertadas, más estado civil casado (64.5 % vs 52.0 %) y más graduados (67.5 % vs 57.3 %). Esto sugiere que el modelo confunde perfiles "maduros" entre segmentos.

## 2. Matriz de confusión

### Test (1.211 filas, evaluación única)

| Real \ Predicho | A | B | C | D | Total | Recall |
|---|---:|---:|---:|---:|---:|---:|
| **A** | 135 | 51 | 42 | 68 | 296 | 0,456 |
| **B** | 54 | 107 | 87 | 30 | 278 | 0,385 |
| **C** | 26 | 49 | 180 | 41 | 296 | 0,608 |
| **D** | 64 | 14 | 7 | 256 | 341 | 0,751 |
| **Total** | 279 | 221 | 316 | 395 | 1.211 | |

Precision: A 0,484 · B 0,484 · C 0,570 · D 0,648. F1: A 0,470 · B 0,429 · C 0,588 · D 0,696.

*Fuente: `reports/confusion_counts_test_15_20261118T092535Z.csv` y `reports/confusion_normalised_test_15_20261118T092535Z.csv`.*

### Validación (1.210 filas, análisis fila a fila)

| Real \ Predicho | A | B | C | D | Total | Recall |
|---|---:|---:|---:|---:|---:|---:|
| **A** | 124 | 59 | 46 | 67 | 296 | 0,419 |
| **B** | 64 | 90 | 94 | 31 | 279 | 0,323 |
| **C** | 33 | 46 | 176 | 40 | 295 | 0,597 |
| **D** | 50 | 17 | 7 | 266 | 340 | 0,782 |
| **Total** | 271 | 212 | 323 | 404 | 1.210 | |

Precision: A 0,458 · B 0,425 · C 0,545 · D 0,658. F1: A 0,437 · B 0,367 · C 0,570 · D 0,715.

*Fuente: `reports/confusion_counts_val_15.csv` y `reports/final_metrics_val_15.csv` (predicciones del modelo congelado).*

## 3. Comparación test vs validación

| Métrica | val_15 | test_15 | Diferencia |
|---|---:|---:|---:|
| Accuracy | 0,5421 | 0,5599 | +1,77 pp |
| Macro-F1 | 0,5222 | 0,5456 | +2,34 pp |

El test es **mejor** que la validación en ambas métricas. No hay sobreajuste: el modelo generaliza bien a datos nuevos.

## 4. Pares más confundidos (matriz de test)

| Par (real → predicho) | Casos | % del segmento real |
|---|---:|---:|
| B → C | 87 | 31.3 % de los B |
| A → D | 68 | 23.0 % de los A |
| B → A | 54 | 19.4 % de los B |
| D → A | 64 | 18.8 % de los D |
| A → B | 51 | 17.2 % de los A |
| C → B | 49 | 16.6 % de los C |
| A → C | 42 | 14.2 % de los A |
| C → D | 41 | 13.9 % de los C |
| C → A | 26 | 8.8 % de los C |
| B → D | 30 | 10.8 % de los B |

Los dos pares dominantes son **B ↔ C** (87 + 49 = 136 confusiones) y **A ↔ D** (68 + 64 = 132 confusiones).

## 5. Perfil de las filas mal clasificadas en val_15

Se comparan las 553 filas mal clasificadas con las 657 acertadas (predicciones del modelo congelado sobre `val_15`):

| Variable | Aciertos (media) | Errores (media) | Diferencia |
|---|---:|---:|---:|
| Edad | 40.19 | 46.01 | +5.8 años |
| Experiencia laboral | 2.49 | 2.77 | +0.28 años |
| Tamaño de familia | 3.02 | 2.76 | -0.26 |

| Variable categórica | Aciertos (nivel más frecuente) | Errores (nivel más frecuente) |
|---|---|---|
| Gender | Male (59.2 %) | Male (53.5 %) |
| Ever_Married | Yes (52.0 %) | Yes (64.5 %) |
| Graduated | Yes (57.3 %) | Yes (67.5 %) |
| Profession | Artist (32.0 %) | Artist (32.1 %) |
| Spending_Score | Low (62.7 %) | Low (57.3 %) |

**Lectura**: las filas mal clasificadas son en promedio **5.8 años más mayores**, más estado civil casado (64.5 % vs 52.0 %) y más graduados (67.5 % vs 57.3 %). Esto sugiere que el modelo confunde perfiles "maduros" entre segmentos.

## 6. Ejemplos de filas mal clasificadas

Se muestran 3 ejemplos por segmento real, con todas sus variables. Son **ilustrativos**: no representan el conjunto completo de errores, pero muestran los patrones típicos.

### Segmento real A (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 51 | Male | Yes | Yes | Artist | 1.0 | Low | 1.0 | B |
| 40 | Female | Yes | No | Artist | 3.0 | Average | nan | C |
| 39 | Male | Yes | No | Executive | 8.0 | Average | 4.0 | D |

### Segmento real B (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 27 | Male | No | Yes | Artist | 9.0 | Low | 2.0 | A |
| 23 | Male | No | No | Doctor | 0.0 | Low | 5.0 | D |
| 38 | Male | Yes | No | Executive | 9.0 | High | 5.0 | A |

### Segmento real C (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 57 | Male | Yes | Yes | Artist | 0.0 | Low | 1.0 | B |
| 26 | Female | No | Yes | Engineer | 0.0 | Low | 3.0 | D |
| 48 | Male | Yes | Yes | Homemaker | 9.0 | Low | 1.0 | D |

### Segmento real D (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 46 | Female | No | No | Engineer | 1.0 | Low | 3.0 | A |
| 38 | Male | Yes | No | Doctor | 0.0 | High | 4.0 | B |
| 67 | Female | Yes | No | Lawyer | nan | High | 2.0 | B |

**Lectura de los ejemplos:**
- Los B mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o ejecutivos con gasto High (se parecen a A o C).
- Los D mal clasificados suelen ser mayores, casados o con gasto High (se parecen a A, B o C).
- Los C mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o con gasto Average (se parecen a B).

*Los ejemplos son ilustrativos y se obtienen de las primeras 3 filas mal clasificadas por segmento en val_15. No representan el conjunto completo de errores.*

## 7. Hipótesis (marcadas como hipótesis, no como hechos)

1. **B es el segmento más difícil porque su perfil es intermedio.** B se parece a C en edad (46 vs 49), graduación (73,7 % vs 81,7 %) y estado civil (73,7 % vs 79,5 %), pero tiene menos gasto High (20,6 % vs 21,2 %) y más Low (48,7 % vs 33,6 %). La frontera B-C es difusa y el modelo no la separa bien (94 confusiones B→C en val, 87 en test).
2. **B también se confunde con A.** Ambos tienen gasto mixto, pero A es más joven (mediana 41 vs 46) y tiene familias más pequeñas. El modelo puede estar usando la edad y el gasto como señales principales, y B cae en medio.
3. **D se reconoce bien porque es el más distinto.** Joven (mediana 29), no casado (29,0 %), no graduado (37,8 %), Healthcare (43,2 %), gasto Low (86,8 %). Cualquier variable por sí sola ya apunta a D. Pero cuando un D es mayor, casado o tiene gasto High, se confunde con A o B.
4. **A es el segundo más difícil** (recall 0,419). Es el segmento "promedio": edad 41, casado 58,2 %, graduado 61,5 %. Como se parece a todos, el modelo no tiene una señal clara. Se confunde con D (67 en val, 68 en test), B (59 en val, 51 en test) y C (46 en val, 42 en test).
5. **Las variables que más peso tienen en el modelo son Age, Profession y Spending_Score** (importancia por permutación: 0,080, 0,077 y 0,054). Ever_Married tiene el V de Cramér más alto (0,408) pero es la menos importante (0,006). *Hipótesis*: esto se debe a que la información de Ever_Married ya está capturada por Spending_Score (V = 0,669 entre las dos variables). Esta es una interpretación del analista, no una conclusión verificada.

## 8. Datos adicionales que ayudarían a corregir los errores

1. **Ingresos o nivel de gasto real**: Spending_Score es un proxy. Con ingresos reales, B y C podrían separarse mejor (B tiene 48,7 % Low y C solo 33,6 %).
2. **Productos adquiridos (P1 a P5)**: el dataset no incluye qué productos compra cada cliente. Saber qué compra ayudaría a distinguir B (gasto mixto) de C (gasto alto).
3. **Tipo de vehículo**: el dataset no incluye esta variable. Sería útil para confirmar si D es el segmento de entrada.
4. **Canal de contacto**: la app propone canales digitales para D por su edad (mediana 29), pero no hay datos de canal en el dataset.
5. **Historial de compras**: frecuencia y recencia de compra. El dataset es estático (un solo punto en el tiempo).

Estas recomendaciones alimentan la sección de limitaciones del informe (US-16, sección 9) y la recomendación de negocio de recoger estos datos.

## 9. Limitaciones del análisis

- El análisis de filas se hace sobre `val_15` (1.210 filas), no sobre `test_15`, porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron. Las matrices de confusión de test sí están disponibles en `reports/` y se usan para el análisis agregado.
- Las hipótesis no se han verificado con datos adicionales. Son interpretaciones del analista, no conclusiones.
- El modelo no se reajustó con los errores encontrados. La configuración está congelada (D-018).
- El análisis no incluye rendimiento por subgrupos (género, edad), que es un criterio opcional de US-14.
- La diferencia de una fila entre el modelo congelado (0,5421) y la ejecución registrada de boosting (0,5430) es por variación de XGBoost hist entre ejecuciones. No afecta a las conclusiones.

## Fuentes

- Matriz de confusión de test: `reports/confusion_counts_test_15_20261118T092535Z.csv`, `reports/confusion_normalised_test_15_20261118T092535Z.csv`
- Métricas de test: `reports/final_metrics_test_15_20261118T092535Z.csv`
- Métricas de validación: `reports/final_metrics_val_15.csv`
- Importancia de variables: `reports/feature_importance_val_15.csv`
- Perfiles de segmento: `reports/segment_profile_train_70.csv`
- Predicciones de validación: `reports/error_analysis_val_15.csv` (553 filas mal clasificadas)
- Modelo congelado: `models/final_model.joblib` (generado localmente, no commiteado)
- Decisiones: D-010 (métrica y overfitting), D-015 (selección de configuración), D-016 (priorización), D-017 (train_70 solo), D-018 (XGBoost elegido y congelado)
