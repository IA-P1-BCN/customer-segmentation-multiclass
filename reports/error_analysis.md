# Análisis de errores del modelo (US-14)

**Modelo evaluado:** XGBoost congelado (min_child_weight=5, 300 árboles, depth 3, lr 0,05), entrenado solo con `train_70` (D-017). Evaluación única en `test_15` (US-12, issue #29). El análisis de filas se hace sobre `val_15` (1.210 filas), porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron.

## 1. Resumen ejecutivo

El modelo acierta el **54,3 % de los clientes de validación** (657 de 1.210) y el **56,0 % en test** (0,5599). El segmento más difícil es **B** (recall 0,326, F1 0,369): dos de cada tres clientes B se predicen como otro segmento. El más fácil es **D** (recall 0,785, F1 0,714). El par más confundido es **B → C** (95 casos), seguido de **A → D** (69) y **B → A** (63).

Los errores no son aleatorios: las filas mal clasificadas tienen en promedio **6 años más** que las acertadas, más estado civil casado (64,5 % vs 52,0 %) y más graduados (67,5 % vs 57,3 %). Esto sugiere que el modelo confunde perfiles "maduros" entre segmentos.

## 2. Matriz de confusión

### Test (1.211 filas, evaluación única)

| Real \ Predicho | A | B | C | D |
|---|---:|---:|---:|---:|
| **A** | (ver `confusion_counts_test_15_*.csv`) | | | |
| **B** | | | | |
| **C** | | | | |
| **D** | | | | |

*Fuente: `reports/confusion_counts_test_15_20261118T092535Z.csv` y `reports/confusion_normalised_test_15_20261118T092535Z.csv`.*

### Validación (1.210 filas, análisis fila a fila)

| Real \ Predicho | A | B | C | D | Total | Recall |
|---|---:|---:|---:|---:|---:|---:|
| **A** | 122 | 60 | 45 | 69 | 296 | 0,412 |
| **B** | 63 | 91 | 95 | 30 | 279 | 0,326 |
| **C** | 30 | 46 | 177 | 42 | 295 | 0,600 |
| **D** | 49 | 17 | 7 | 267 | 340 | 0,785 |
| **Total** | 264 | 214 | 324 | 408 | 1.210 | |

Precision: A 0,462 · B 0,425 · C 0,546 · D 0,654. F1: A 0,436 · B 0,369 · C 0,572 · D 0,714.

## 3. Comparación test vs validación

| Métrica | val_15 | test_15 | Diferencia |
|---|---:|---:|---:|
| Accuracy | 0,5421 | 0,5599 | +1,77 pp |
| Macro-F1 | 0,5222 | 0,5456 | +2,34 pp |

El test es **mejor** que la validación en ambas métricas. No hay sobreajuste: el modelo generaliza bien a datos nuevos.

## 4. Pares más confundidos

| Par (real → predicho) | Casos | % del segmento real |
|---|---:|---:|
| B → C | 95 | 34,1 % de los B |
| A → D | 69 | 23,3 % de los A |
| B → A | 63 | 22,6 % de los B |
| A → B | 60 | 20,3 % de los A |
| D → A | 49 | 14,4 % de los D |
| C → B | 46 | 15,6 % de los C |
| A → C | 45 | 15,2 % de los A |
| C → D | 42 | 14,2 % de los C |

Los dos pares dominantes son **B ↔ C** (95 + 46 = 141 confusiones) y **A ↔ D** (69 + 49 = 118 confusiones).

## 5. Perfil de las filas mal clasificadas

Se comparan las 553 filas mal clasificadas con las 657 acertadas en `val_15`:

| Variable | Aciertos (media) | Errores (media) | Diferencia |
|---|---:|---:|---:|
| Edad | 40,19 | 46,01 | +5,8 años |
| Experiencia laboral | 2,49 | 2,77 | +0,28 años |
| Tamaño de familia | 3,02 | 2,76 | −0,26 |

| Variable categórica | Aciertos (nivel más frecuente) | Errores (nivel más frecuente) |
|---|---|---|
| Género | Male (59,2 %) | Male (53,5 %) |
| Estado civil | Yes (52,0 %) | Yes (64,5 %) |
| Graduado | Yes (57,3 %) | Yes (67,5 %) |
| Profesión | Artist (32,0 %) | Artist (32,1 %) |
| Gasto | Low (62,7 %) | Low (57,3 %) |

**Lectura**: las filas mal clasificadas son en promedio **más mayores, más casadas y más graduadas** que las acertadas. Esto sugiere que el modelo tiene más dificultad con perfiles "maduros" (B y C), que son los que más se parecen entre sí. El gasto es similar en ambos grupos, así que no es el factor que diferencia aciertos de errores.

## 6. Ejemplos de filas mal clasificadas

### Segmento real A (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 51 | Male | Yes | Yes | Artist | 1 | Low | 1 | B |
| 40 | Female | Yes | No | Artist | 3 | Average | nan | C |
| 39 | Male | Yes | No | Executive | 8 | Average | 4 | D |

### Segmento real B (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 27 | Male | No | Yes | Artist | 9 | Low | 2 | A |
| 23 | Male | No | No | Doctor | 0 | Low | 5 | D |
| 38 | Male | Yes | No | Executive | 9 | High | 5 | A |

### Segmento real C (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 57 | Male | Yes | Yes | Artist | 0 | Low | 1 | B |
| 26 | Female | No | Yes | Engineer | 0 | Low | 3 | D |
| 48 | Male | Yes | Yes | Homemaker | 9 | Low | 1 | D |

### Segmento real D (predicho como otra cosa)

| Edad | Género | Casado | Graduado | Profesión | Experiencia | Gasto | Familia | Predicho |
|---|---|---|---|---|---|---|---|---|
| 46 | Female | No | No | Engineer | 1 | Low | 3 | A |
| 38 | Male | Yes | No | Doctor | 0 | High | 4 | B |
| 67 | Female | Yes | No | Lawyer | nan | High | 2 | B |

**Lectura de los ejemplos:**
- Los B mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o ejecutivos con gasto High (se parecen a A o C).
- Los D mal clasificados suelen ser mayores, casados o con gasto High (se parecen a A, B o C).
- Los C mal clasificados suelen ser jóvenes no casados con gasto Low (se parecen a D) o con gasto Average (se parecen a B).

## 7. Hipótesis (marcadas como hipótesis, no como hechos)

1. **B es el segmento más difícil porque su perfil es intermedio.** B se parece a C en edad (46 vs 49), graduación (73,7 % vs 81,7 %) y estado civil (73,7 % vs 79,5 %), pero tiene menos gasto High (20,6 % vs 21,2 %) y más Low (48,7 % vs 33,6 %). La frontera B-C es difusa y el modelo no la separa bien (95 confusiones B→C).
2. **B también se confunde con A** (63 confusiones B→A). Ambos tienen gasto mixto, pero A es más joven (mediana 41 vs 46) y tiene familias más pequeñas. El modelo puede estar usando la edad y el gasto como señales principales, y B cae en medio.
3. **D se reconoce bien porque es el más distinto.** Joven (mediana 29), no casado (29,0 %), no graduado (37,8 %), Healthcare (43,2 %), gasto Low (86,8 %). Cualquier variable por sí sola ya apunta a D. Pero cuando un D es mayor, casado o tiene gasto High, se confunde con A o B.
4. **A es el segundo más difícil** (recall 0,412). Es el segmento "promedio": edad 41, casado 58,2 %, graduado 61,5 %. Como se parece a todos, el modelo no tiene una señal clara. Se confunde con D (69), B (60) y C (45).
5. **Las variables que más peso tienen en el modelo son Age, Profession y Spending_Score** (importancia por permutación: 0,080, 0,077 y 0,054). Pero Ever_Married, que tiene el V de Cramér más alto (0,408), es la menos importante (0,006) porque su información ya está capturada por Spending_Score (V = 0,669 entre las dos).

## 8. Datos adicionales que ayudarían a corregir los errores

1. **Ingresos o nivel de gasto real**: Spending_Score es un proxy. Con ingresos reales, B y C se separarían mejor (B tiene 48,7 % Low y C solo 33,6 %).
2. **Productos adquiridos (P1 a P5)**: el dataset no incluye qué productos compra cada cliente. Saber qué compra ayudaría a distinguir B (gasto mixto) de C (gasto alto).
3. **Tipo de vehículo**: D tiene más vehículos de gama baja, pero no se sabe cuál. Esto ayudaría a confirmar la hipótesis de que D es el segmento de entrada.
4. **Canal de contacto**: la app propone canales digitales para D por su edad (mediana 29), pero no hay datos de canal en el dataset.
5. **Historial de compras**: frecuencia y recencia de compra. El dataset es estático (un solo punto en el tiempo).

Estas recomendaciones alimentan la sección de limitaciones del informe (US-16, sección 9) y la recomendación de negocio de recoger estos datos.

## 9. Limitaciones del análisis

- El análisis de filas se hace sobre `val_15` (1.210 filas), no sobre `test_15`, porque `test_15` es de un solo uso y las predicciones fila a fila no se guardaron. Las matrices de confusión de test sí están disponibles en `reports/` y se usan para el análisis agregado.
- Las hipótesis no se han verificado con datos adicionales. Son interpretaciones del analista, no conclusiones.
- El modelo no se reajustó con los errores encontrados. La configuración está congelada (D-018).
- El análisis no incluye rendimiento por subgrupos (género, edad), que es un criterio opcional de US-12.

## Fuentes

- Matriz de confusión de test: `reports/confusion_counts_test_15_20261118T092535Z.csv`, `reports/confusion_normalised_test_15_20261118T092535Z.csv`
- Métricas de test: `reports/final_metrics_test_15_20261118T092535Z.csv`
- Métricas de validación: `reports/final_metrics_val_15.csv`
- Importancia de variables: `reports/feature_importance_val_15.csv`
- Perfiles de segmento: `reports/segment_profile_train_70.csv`
- Predicciones de validación: `reports/error_analysis_val_15.csv` (553 filas mal clasificadas)
- Modelo congelado: `models/final_model.joblib` (generado localmente, no commiteado)
- Decisiones: D-010 (métrica y overfitting), D-015 (selección de configuración), D-016 (priorización), D-017 (train_70 solo), D-018 (XGBoost elegido y congelado)