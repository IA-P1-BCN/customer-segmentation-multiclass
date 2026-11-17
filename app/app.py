"""Streamlit prediction application (US-15, issue #35).

Run from the repository root with:

    python -m streamlit run app/app.py

Phase 1 provides the form, input validation, campaign loading and the model
seam. The frozen model itself belongs to US-11 (issue #27); until it is
available, the form validates a record and explains that prediction is pending.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
except ImportError as exc:
    raise SystemExit(
        "Streamlit no está instalado. Instálalo en el entorno del proyecto antes "
        "de ejecutar la app: python -m pip install streamlit"
    ) from exc

from app.utils.campaigns import CampaignConfigError, load_campaigns
from app.utils.model import PredictionError, predict_segment
from app.utils.validation import (
    CATEGORY_OPTIONS,
    FIELD_LABELS,
    INTEGER_RANGES,
    ValidationError,
    build_feature_frame,
)

GENDER_LABELS = {"Female": "Femenino", "Male": "Masculino"}
SPENDING_LABELS = {"Low": "Bajo", "Average": "Medio", "High": "Alto"}
YES_NO_LABELS = {"Yes": "Sí", "No": "No"}
PROFESSION_LABELS = {
    "Artist": "Artista",
    "Doctor": "Doctor/a",
    "Engineer": "Ingeniería",
    "Entertainment": "Entretenimiento",
    "Executive": "Dirección",
    "Healthcare": "Salud",
    "Homemaker": "Hogar",
    "Lawyer": "Abogacía",
    "Marketing": "Marketing",
}
OPTIONAL_VALUE = "No especificado"


def _optional(value: Any) -> Any:
    return None if value == OPTIONAL_VALUE else value


def _render_required_fields() -> dict[str, Any]:
    age_min, age_max = INTEGER_RANGES["Age"]
    age_col, gender_col, spending_col = st.columns(3)
    with age_col:
        age = st.number_input(
            "Edad",
            min_value=age_min,
            max_value=age_max,
            value=35,
            step=1,
        )
    with gender_col:
        gender = st.selectbox(
            "Género",
            options=list(CATEGORY_OPTIONS["Gender"]),
            format_func=lambda value: GENDER_LABELS.get(value, value),
        )
    with spending_col:
        spending = st.selectbox(
            "Nivel de gasto",
            options=list(CATEGORY_OPTIONS["Spending_Score"]),
            format_func=lambda value: SPENDING_LABELS.get(value, value),
        )
    return {"Age": age, "Gender": gender, "Spending_Score": spending}


def _render_optional_fields() -> dict[str, Any]:
    with st.expander("Datos opcionales (se imputan si faltan)"):
        first, second = st.columns(2)

        with first:
            married = st.selectbox(
                "Estado civil",
                options=[OPTIONAL_VALUE, *CATEGORY_OPTIONS["Ever_Married"]],
                format_func=lambda value: YES_NO_LABELS.get(value, value),
            )
            graduated = st.selectbox(
                "Graduado/a",
                options=[OPTIONAL_VALUE, *CATEGORY_OPTIONS["Graduated"]],
                format_func=lambda value: YES_NO_LABELS.get(value, value),
            )
            profession = st.selectbox(
                "Profesión",
                options=[OPTIONAL_VALUE, *CATEGORY_OPTIONS["Profession"]],
                format_func=lambda value: PROFESSION_LABELS.get(value, value),
            )

        with second:
            work_min, work_max = INTEGER_RANGES["Work_Experience"]
            work_experience = st.selectbox(
                "Experiencia laboral",
                options=[OPTIONAL_VALUE, *range(work_min, work_max + 1)],
                format_func=lambda value: (
                    value if value == OPTIONAL_VALUE else f"{value} años"
                ),
            )
            family_min, family_max = INTEGER_RANGES["Family_Size"]
            family_size = st.selectbox(
                "Tamaño del hogar",
                options=[OPTIONAL_VALUE, *range(family_min, family_max + 1)],
                format_func=lambda value: (
                    value if value == OPTIONAL_VALUE else f"{value} personas"
                ),
            )
            var_1 = st.selectbox(
                "Var_1",
                options=[OPTIONAL_VALUE, *CATEGORY_OPTIONS["Var_1"]],
            )

    return {
        "Ever_Married": _optional(married),
        "Graduated": _optional(graduated),
        "Profession": _optional(profession),
        "Work_Experience": _optional(work_experience),
        "Family_Size": _optional(family_size),
        "Var_1": _optional(var_1),
    }


def main(predictor: Any = None) -> None:
    """Render the application; ``predictor`` is injectable for tests."""
    st.set_page_config(page_title="Segmentación de clientes", layout="centered")
    st.title("Segmentación de clientes")
    st.write(
        "Completa los datos del cliente para estimar su segmento y consultar "
        "la campaña propuesta."
    )

    try:
        catalog = load_campaigns()
    except CampaignConfigError as exc:
        st.error(f"No se pudo cargar la configuración de campañas: {exc}")
        return

    st.caption(f"Estado de las campañas: {catalog.status}. Fuente: {catalog.source}.")
    st.warning(catalog.disclaimer)

    with st.form("customer_form"):
        payload: dict[str, Any] = {}
        payload.update(_render_required_fields())
        payload.update(_render_optional_fields())
        submitted = st.form_submit_button("Predecir segmento")

    if not submitted:
        return

    try:
        features = build_feature_frame(payload)
    except ValidationError as exc:
        st.error("Revisa los datos del formulario:")
        for field, message in exc.errors.items():
            label = FIELD_LABELS.get(field, field)
            st.write(f"- **{label}:** {message}")
        return

    st.success("Datos validados correctamente.")
    if predictor is None:
        st.info(
            "Fase 1: el formulario y la validación están listos, pero el modelo "
            "congelado aún no está conectado. La predicción se habilitará cuando "
            "US-11 publique el artefacto."
        )
        return

    try:
        segment = predict_segment(predictor, features)
        campaign = catalog.get(segment)
    except (PredictionError, CampaignConfigError) as exc:
        st.error(str(exc))
        return

    st.metric("Segmento predicho", segment)
    st.subheader("Campaña propuesta")
    st.write(campaign.campaign)
    st.caption(
        "Campaña en borrador procedente de US-13; pendiente de aprobación (D-016)."
    )


if __name__ == "__main__":
    main()
