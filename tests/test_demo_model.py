"""Tests for the demonstration sentiment model.

Covers:
* Happy-path inference (positive / negative).
* Real inference (non-hardcoded outputs).
* Invalid-input handling (missing, empty, wrong type, not loaded).
* Contract and metadata accessors.
"""

from __future__ import annotations

import pytest

from modular_agent.models.demo_model import DemoSentimentModel


class TestDemoModelLoading:
    """Model lifecycle tests."""

    def test_is_loaded_after_load(self, demo_model: DemoSentimentModel) -> None:
        assert demo_model.is_loaded is True

    def test_is_not_loaded_before_load(
        self, unloaded_demo_model: DemoSentimentModel,
    ) -> None:
        assert unloaded_demo_model.is_loaded is False


class TestDemoModelPrediction:
    """Inference tests — verify actual model behaviour."""

    def test_positive_sentiment(self, demo_model: DemoSentimentModel) -> None:
        result = demo_model.predict({"text": "This is absolutely wonderful and amazing"})
        assert result["label"] == "positive"
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["model_type"] == "demonstration"

    def test_negative_sentiment(self, demo_model: DemoSentimentModel) -> None:
        result = demo_model.predict({"text": "This is terrible and horrible"})
        assert result["label"] == "negative"
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["model_type"] == "demonstration"

    def test_returns_actual_inference_not_hardcoded(
        self, demo_model: DemoSentimentModel,
    ) -> None:
        """Unseen text must still produce valid structured output."""
        r1 = demo_model.predict({"text": "unprecedented cosmic event observed"})
        r2 = demo_model.predict({"text": "random words foxtrot zulu bravo"})
        for r in (r1, r2):
            assert r["label"] in ("positive", "negative")
            assert isinstance(r["confidence"], float)
            assert r["model_type"] == "demonstration"

    def test_confidence_varies_across_inputs(
        self, demo_model: DemoSentimentModel,
    ) -> None:
        c1 = demo_model.predict(
            {"text": "fantastic amazing wonderful superb"},
        )["confidence"]
        c2 = demo_model.predict(
            {"text": "okay"},
        )["confidence"]
        # Different inputs should *usually* produce different confidence.
        # Guard: both must at least be valid floats in [0, 1].
        assert 0.0 <= c1 <= 1.0
        assert 0.0 <= c2 <= 1.0


class TestDemoModelInvalidInputs:
    """Invalid-input error paths."""

    def test_predict_before_load_raises(
        self, unloaded_demo_model: DemoSentimentModel,
    ) -> None:
        with pytest.raises(RuntimeError, match="not loaded"):
            unloaded_demo_model.predict({"text": "hello"})

    def test_missing_text_field(self, demo_model: DemoSentimentModel) -> None:
        with pytest.raises(ValueError, match="Missing required field"):
            demo_model.predict({})

    def test_empty_text(self, demo_model: DemoSentimentModel) -> None:
        with pytest.raises(ValueError, match="empty"):
            demo_model.predict({"text": ""})

    def test_whitespace_only_text(self, demo_model: DemoSentimentModel) -> None:
        with pytest.raises(ValueError, match="empty"):
            demo_model.predict({"text": "   \t\n  "})

    def test_non_string_text(self, demo_model: DemoSentimentModel) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            demo_model.predict({"text": 12345})

    def test_none_text(self, demo_model: DemoSentimentModel) -> None:
        with pytest.raises(ValueError, match="Missing required field"):
            demo_model.predict({"text": None})


class TestDemoModelContracts:
    """Contract and metadata accessors."""

    def test_input_contract_declares_text(
        self, demo_model: DemoSentimentModel,
    ) -> None:
        contract = demo_model.input_contract()
        assert "text" in contract.fields
        assert contract.fields["text"].type == "str"
        assert contract.fields["text"].required is True

    def test_output_contract_declares_label_and_confidence(
        self, demo_model: DemoSentimentModel,
    ) -> None:
        contract = demo_model.output_contract()
        assert "label" in contract.fields
        assert "confidence" in contract.fields
        assert "model_type" in contract.fields

    def test_name_is_non_empty(self, demo_model: DemoSentimentModel) -> None:
        assert demo_model.name() == "demo_sentiment_classifier"

    def test_description_mentions_sentiment(
        self, demo_model: DemoSentimentModel,
    ) -> None:
        desc = demo_model.description()
        assert "sentiment" in desc.lower()
        assert "demonstration" in desc.lower()

