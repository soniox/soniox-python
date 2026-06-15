"""Tests for type validators and input coercion in soniox.types."""

from __future__ import annotations

import pytest

from soniox.types import (
    RealtimeSTTConfig,
    StructuredContext,
    StructuredContextGeneralItem,
    StructuredContextTranslationTerm,
)


# ---------------------------------------------------------------------------
# StructuredContext dict-input coercion
# ---------------------------------------------------------------------------


def test_structured_context_general_accepts_dict() -> None:
    ctx = StructuredContext(general={"domain": "Healthcare", "topic": "Radiology"})
    assert ctx.general == [
        StructuredContextGeneralItem(key="domain", value="Healthcare"),
        StructuredContextGeneralItem(key="topic", value="Radiology"),
    ]


def test_structured_context_translation_terms_accepts_dict() -> None:
    ctx = StructuredContext(translation_terms={"Mr. Smith": "Sr. Smith"})
    assert ctx.translation_terms == [
        StructuredContextTranslationTerm(source="Mr. Smith", target="Sr. Smith"),
    ]


def test_structured_context_general_keeps_typed_list_unchanged() -> None:
    items = [StructuredContextGeneralItem(key="domain", value="Healthcare")]
    ctx = StructuredContext(general=items)
    assert ctx.general == items


# ---------------------------------------------------------------------------
# RealtimeSTTConfig raw-format validation
# ---------------------------------------------------------------------------


def test_raw_format_requires_sample_rate_and_channels() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-v5", audio_format="pcm_s16le")
    msg = str(exc.value)
    assert "sample_rate" in msg
    assert "num_channels" in msg


def test_raw_format_requires_sample_rate_only() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-v5", audio_format="pcm_s16le", num_channels=1)
    assert "sample_rate" in str(exc.value)


def test_raw_format_requires_num_channels_only() -> None:
    with pytest.raises(ValueError) as exc:
        RealtimeSTTConfig(model="stt-rt-v5", audio_format="pcm_s16le", sample_rate=16000)
    assert "num_channels" in str(exc.value)


def test_raw_format_with_both_succeeds() -> None:
    cfg = RealtimeSTTConfig(model="stt-rt-v5", audio_format="pcm_s16le", sample_rate=16000, num_channels=1)
    assert cfg.audio_format == "pcm_s16le"
    assert cfg.sample_rate == 16000
    assert cfg.num_channels == 1
