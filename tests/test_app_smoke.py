"""Smoke test for the Streamlit entry point with a fake streamlit module.

The test injects a minimal stub to exercise ``app.app.main`` without a browser.
It never loads the real frozen-model artefact.
"""

from __future__ import annotations

import sys
import types
from typing import Any, Self


class _FakeContext:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False


class _FakeColumn(_FakeContext):
    def __init__(self, parent: FakeStreamlit) -> None:
        self._parent = parent

    def __getattr__(self, name: str) -> Any:
        return getattr(self._parent, name)


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.messages: list[str] = []

    def set_page_config(self, **kwargs: Any) -> None:
        pass

    def title(self, text: str) -> None:
        self.messages.append(text)

    def write(self, text: str) -> None:
        self.messages.append(text)

    def caption(self, text: str) -> None:
        self.messages.append(text)

    def warning(self, text: str) -> None:
        self.messages.append(text)

    def error(self, text: str) -> None:
        self.messages.append(text)

    def info(self, text: str) -> None:
        self.messages.append(text)

    def success(self, text: str) -> None:
        self.messages.append(text)

    def metric(self, label: str, value: object) -> None:
        self.messages.append(f"{label}: {value}")

    def subheader(self, text: str) -> None:
        self.messages.append(text)

    def columns(self, spec: int | list[object]) -> list[_FakeColumn]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeColumn(self) for _ in range(count)]

    def form(self, key: str) -> _FakeContext:
        return _FakeContext()

    def expander(self, label: str) -> _FakeContext:
        return _FakeContext()

    def number_input(self, label: str, **kwargs: Any) -> Any:
        return kwargs["value"]

    def selectbox(self, label: str, options: list[Any], **kwargs: Any) -> Any:
        return options[0]

    def form_submit_button(self, label: str) -> bool:
        return True


class FakePredictor:
    def predict(self, features: Any) -> list[str]:
        return ["B"]


def test_main_renders_prediction_with_injected_predictor(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    app_module.main(FakePredictor())

    text = "\n".join(fake.messages)
    assert "Segmento predicho: B" in text
    assert "Oferta con opciones en varios niveles de precio." in text
    assert "hipótesis de negocio" in text


def test_main_renders_prediction_without_injected_predictor(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    monkeypatch.setattr(app_module, "load_predictor", lambda: FakePredictor())
    app_module.main()

    text = "\n".join(fake.messages)
    assert "Datos validados correctamente." in text
    assert "Segmento predicho: B" in text
    assert "Campaña propuesta" in text
    assert "US-11" not in text


def test_main_explains_how_to_generate_a_missing_artifact(monkeypatch, tmp_path):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    monkeypatch.setattr(
        "app.utils.model.DEFAULT_MODEL_PATH", tmp_path / "missing.joblib"
    )
    sys.modules.pop("app.app", None)

    import app.app as app_module

    app_module.main()

    text = "\n".join(fake.messages)
    assert "Datos validados correctamente." in text
    assert "No se encontró el modelo congelado." in text
    assert "python -m src.compare_models --stage freeze --model boosting" in text


def test_main_displays_validation_errors_with_spanish_field_labels(monkeypatch):
    fake = FakeStreamlit()
    fake.number_input = lambda label, **kwargs: 17  # 17 is outside the valid Age range [18, 89]
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    app_module.main()

    text = "\n".join(fake.messages)
    assert "Revisa los datos del formulario:" in text
    assert "- **Edad:** Debe estar entre 18 y 89." in text
    assert "Datos validados correctamente." not in text


def test_main_uses_the_model_loader_when_predictor_is_not_injected(monkeypatch):
    calls: list[bool] = []

    def fake_loader():
        calls.append(True)
        return FakePredictor()

    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    monkeypatch.setattr(app_module, "load_predictor", fake_loader)
    app_module.main()

    text = "\n".join(fake.messages)
    assert calls == [True]
    assert "Segmento predicho: B" in text
    assert "Oferta con opciones en varios niveles de precio." in text
    assert "US-11" not in text


def test_main_explains_when_the_model_artifact_cannot_be_loaded(monkeypatch):
    from app.utils.model import ModelArtifactError

    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    def failing_loader():
        raise ModelArtifactError("No se pudo cargar el artefacto del modelo.")

    monkeypatch.setattr(app_module, "load_predictor", failing_loader)
    app_module.main()

    text = "\n".join(fake.messages)
    assert "No se pudo cargar el modelo congelado" in text
    assert "No se pudo cargar el artefacto del modelo." in text
    assert "brew install libomp" in text
    assert "Segmento predicho:" not in text


def test_main_explains_when_joblib_is_not_installed(monkeypatch):
    from app.utils.model import ModelArtifactError

    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    def failing_loader():
        raise ModelArtifactError("joblib no está instalado.")

    monkeypatch.setattr(app_module, "load_predictor", failing_loader)
    app_module.main()

    text = "\n".join(fake.messages)
    assert "No se pudo cargar el modelo congelado" in text
    assert "joblib no está instalado." in text
    assert "Segmento predicho:" not in text
