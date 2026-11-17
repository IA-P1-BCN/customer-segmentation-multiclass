"""Smoke test for the Streamlit entry point with a fake streamlit module.

The real dependency is not installed in the current environment, so this test
injects a minimal stub to exercise ``app.app.main`` without a browser.
"""

from __future__ import annotations

import sys
import types
from typing import Any

import pytest


class _FakeContext:
    def __enter__(self) -> "_FakeContext":
        return self

    def __exit__(self, *args: object) -> bool:
        return False


class _FakeColumn(_FakeContext):
    def __init__(self, parent: "FakeStreamlit") -> None:
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
    assert "Offer with options at several price levels." in text
    assert "Campaña en borrador" in text


def test_main_explains_that_the_model_is_pending(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    sys.modules.pop("app.app", None)

    import app.app as app_module

    app_module.main()

    text = "\n".join(fake.messages)
    assert "Datos validados correctamente." in text
    assert "US-11" in text


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
