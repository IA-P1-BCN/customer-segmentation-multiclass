"""Campaign catalogue loader for the prediction application (US-15, issue #35).

The campaign texts are the business hypotheses approved in US-13 (PR #69) and
integrated by US-15. They live in ``app/config/campaigns.json`` so the
application can display them without embedding business copy in the code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

__all__ = [
    "Campaign",
    "CampaignCatalog",
    "CampaignConfigError",
    "DEFAULT_CAMPAIGNS_PATH",
    "SEGMENT_LABELS",
    "load_campaigns",
]

SEGMENT_LABELS = ("A", "B", "C", "D")
DEFAULT_CAMPAIGNS_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "campaigns.json"
)


class CampaignConfigError(ValueError):
    """Raised when the campaign catalogue is missing or malformed."""


@dataclass(frozen=True)
class Campaign:
    """Campaign proposal associated with one predicted segment."""

    segment: str
    campaign: str


@dataclass(frozen=True)
class CampaignCatalog:
    """Validated campaign catalogue plus its traceability metadata."""

    status: str
    source: str
    disclaimer: str
    campaigns: Mapping[str, Campaign]

    def get(self, segment: str) -> Campaign:
        """Return the campaign for ``segment`` or raise ``CampaignConfigError``."""
        try:
            return self.campaigns[segment]
        except KeyError as exc:
            raise CampaignConfigError(
                f"No hay campaña configurada para el segmento {segment!r}."
            ) from exc


def _require_text(data: Mapping[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CampaignConfigError(
            f"El campo {key!r} de {context} debe ser un texto no vacío."
        )
    return value.strip()


def load_campaigns(path: str | Path = DEFAULT_CAMPAIGNS_PATH) -> CampaignCatalog:
    """Load and validate the campaign catalogue from ``path``."""
    catalogue_path = Path(path)
    try:
        raw = json.loads(catalogue_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CampaignConfigError(
            f"No se pudo leer el catálogo de campañas en {catalogue_path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CampaignConfigError(
            f"El catálogo de campañas no es JSON válido: {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise CampaignConfigError(
            "El catálogo de campañas debe ser un objeto JSON."
        )

    status = _require_text(raw, "status", "el catálogo")
    source = _require_text(raw, "source", "el catálogo")
    disclaimer = _require_text(raw, "disclaimer", "el catálogo")

    segments = raw.get("segments")
    if not isinstance(segments, dict):
        raise CampaignConfigError(
            "El catálogo debe incluir un objeto 'segments'."
        )

    missing = [segment for segment in SEGMENT_LABELS if segment not in segments]
    extra = [segment for segment in segments if segment not in SEGMENT_LABELS]
    if missing or extra:
        raise CampaignConfigError(
            "Los segmentos configurados deben ser exactamente A, B, C y D; "
            f"faltan {missing} y sobran {extra}."
        )

    campaigns: dict[str, Campaign] = {}
    for segment in SEGMENT_LABELS:
        entry = segments[segment]
        if not isinstance(entry, dict):
            raise CampaignConfigError(
                f"La entrada del segmento {segment!r} debe ser un objeto JSON."
            )
        campaign = _require_text(
            entry, "campaign", f"el segmento {segment!r}"
        )
        campaigns[segment] = Campaign(segment=segment, campaign=campaign)

    return CampaignCatalog(
        status=status,
        source=source,
        disclaimer=disclaimer,
        campaigns=MappingProxyType(campaigns),
    )
