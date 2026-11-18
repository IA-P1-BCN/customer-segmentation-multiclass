"""Tests for the campaign catalogue (US-15, issue #35)."""

from __future__ import annotations

import json

import pytest

from app.utils.campaigns import (
    CampaignConfigError,
    SEGMENT_LABELS,
    load_campaigns,
)


def catalogue_data() -> dict[str, object]:
    return {
        "status": "Borrador",
        "source": "test",
        "disclaimer": "No aprobado",
        "segments": {
            segment: {"campaign": f"Campaña {segment}"} for segment in SEGMENT_LABELS
        },
    }


def write_catalogue(tmp_path, data: object):
    path = tmp_path / "campaigns.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_default_catalogue_has_every_segment_and_traceability():
    catalog = load_campaigns()
    assert tuple(catalog.campaigns) == SEGMENT_LABELS
    assert catalog.status
    assert catalog.source
    assert catalog.disclaimer
    assert "aprobado" in catalog.status.lower()
    assert "PR #69" in catalog.status
    assert "D-016" in catalog.status
    assert "PR #69" in catalog.source
    for segment in SEGMENT_LABELS:
        campaign = catalog.get(segment)
        assert campaign.segment == segment
        assert campaign.campaign


def test_default_campaign_texts_match_the_approved_hypotheses():
    catalog = load_campaigns()
    assert (
        catalog.get("A").campaign
        == "Oferta básica para hogares pequeños, con opciones de entrada."
    )
    assert catalog.get("B").campaign == (
        "Oferta con opciones en varios niveles de precio."
    )
    assert catalog.get("C").campaign == "Oferta de gama media y alta."
    assert catalog.get("D").campaign == "Oferta de entrada a precio asequible."


def test_unknown_segment_raises():
    catalog = load_campaigns()
    with pytest.raises(CampaignConfigError, match="No hay campaña"):
        catalog.get("Z")


def test_missing_file_raises(tmp_path):
    with pytest.raises(CampaignConfigError, match="No se pudo leer"):
        load_campaigns(tmp_path / "missing.json")


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "campaigns.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(CampaignConfigError, match="JSON válido"):
        load_campaigns(path)


@pytest.mark.parametrize("field", ["status", "source", "disclaimer"])
def test_missing_or_empty_metadata_raises(tmp_path, field):
    data = catalogue_data()
    data[field] = "   "
    with pytest.raises(CampaignConfigError, match=field):
        load_campaigns(write_catalogue(tmp_path, data))


def test_missing_segment_raises(tmp_path):
    data = catalogue_data()
    del data["segments"]["D"]
    with pytest.raises(CampaignConfigError, match="faltan"):
        load_campaigns(write_catalogue(tmp_path, data))


def test_extra_segment_raises(tmp_path):
    data = catalogue_data()
    data["segments"]["E"] = {"campaign": "Extra"}
    with pytest.raises(CampaignConfigError, match="sobran"):
        load_campaigns(write_catalogue(tmp_path, data))


def test_empty_campaign_raises(tmp_path):
    data = catalogue_data()
    data["segments"]["B"]["campaign"] = " "
    with pytest.raises(CampaignConfigError, match="campaign"):
        load_campaigns(write_catalogue(tmp_path, data))


def test_segment_entry_must_be_an_object(tmp_path):
    data = catalogue_data()
    data["segments"]["C"] = "not-an-object"
    with pytest.raises(CampaignConfigError, match="segmento 'C'"):
        load_campaigns(write_catalogue(tmp_path, data))


def test_catalogue_mapping_is_read_only():
    catalog = load_campaigns()
    with pytest.raises(TypeError):
        catalog.campaigns["A"] = catalog.get("B")
