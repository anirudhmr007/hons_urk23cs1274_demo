"""Built-in demonstration sentiment classifier.

This module ships a lightweight binary sentiment model that exercises the
full :class:`~modular_agent.models.base.ModelAdapter` contract without
requiring any external model files, API keys, or GPU resources.

Architecture
------------
``TfidfVectorizer`` → ``LogisticRegression``  (scikit-learn ``Pipeline``)

The pipeline is **trained at load time** on a small built-in corpus of
~40 labelled English sentences.

Limitations
-----------
* **Not production-grade.**  The training corpus is tiny and hand-crafted.
* Confidence values are raw ``predict_proba`` outputs from logistic
  regression — they are **not calibrated probabilities**.
* Vocabulary is limited to terms present in the training set.
* Only English text is supported.
* The model may produce unexpected labels for very short, ambiguous,
  or out-of-domain inputs.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from modular_agent.models.base import FieldContract, ModelAdapter, ModelContract

logger = logging.getLogger(__name__)

# ── Built-in training data ───────────────────────────────────────────────────
# Intentionally small.  The goal is a *working* demonstration, not accuracy.

_TRAINING_DATA: list[tuple[str, str]] = [
    # ── positive ─────────────────────────────────────────
    ("I love this product, it's amazing!", "positive"),
    ("This is wonderful and fantastic", "positive"),
    ("Great experience, highly recommend", "positive"),
    ("Absolutely brilliant, exceeded expectations", "positive"),
    ("Very happy with this purchase", "positive"),
    ("The quality is excellent", "positive"),
    ("Best thing I've ever bought", "positive"),
    ("Incredible service and support", "positive"),
    ("Makes me smile every time", "positive"),
    ("Outstanding performance and value", "positive"),
    ("Really enjoyed using this", "positive"),
    ("Superb craftsmanship and design", "positive"),
    ("Pleasantly surprised by the quality", "positive"),
    ("Everything works perfectly", "positive"),
    ("Delightful experience from start to finish", "positive"),
    ("I'm very impressed with the results", "positive"),
    ("Exceeded all my expectations", "positive"),
    ("Highly satisfied customer here", "positive"),
    ("Top notch quality and service", "positive"),
    ("Would definitely buy again", "positive"),
    # ── negative ─────────────────────────────────────────
    ("This is terrible, waste of money", "negative"),
    ("Horrible experience, very disappointed", "negative"),
    ("Worst purchase I've ever made", "negative"),
    ("Completely broken and useless", "negative"),
    ("Very poor quality, do not buy", "negative"),
    ("Awful product, returning immediately", "negative"),
    ("Frustrating and difficult to use", "negative"),
    ("Total disaster, nothing works", "negative"),
    ("Extremely unhappy with this", "negative"),
    ("Damaged on arrival, very upset", "negative"),
    ("Cheap materials, fell apart quickly", "negative"),
    ("Customer service was rude and unhelpful", "negative"),
    ("Complete waste of time and money", "negative"),
    ("Absolutely dreadful experience", "negative"),
    ("Would not recommend to anyone", "negative"),
    ("Regret buying this product", "negative"),
    ("Stopped working after one day", "negative"),
    ("Misleading description, very angry", "negative"),
    ("The worst quality I have seen", "negative"),
    ("Terrible value for the price", "negative"),
]


class DemoSentimentModel(ModelAdapter):
    """Demonstration sentiment classifier.

    Performs **actual inference** via a scikit-learn pipeline trained on a
    small built-in corpus.  See the module docstring for full limitations.
    """

    _SUPPORTED_LABELS = ("positive", "negative")

    def __init__(self) -> None:
        super().__init__()
        self._pipeline: Pipeline | None = None

    # ── ModelAdapter interface ───────────────────────────────────────────

    def load(self) -> None:
        """Train the TF-IDF + LogisticRegression pipeline."""
        logger.info("Training demonstration sentiment model …")
        texts = [t for t, _ in _TRAINING_DATA]
        labels = [lab for _, lab in _TRAINING_DATA]

        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                stop_words="english",
            )),
            ("clf", LogisticRegression(
                max_iter=200,
                random_state=42,
                solver="liblinear",
            )),
        ])
        self._pipeline.fit(texts, labels)
        self._loaded = True

        vocab_size = len(self._pipeline.named_steps["tfidf"].vocabulary_)
        logger.info(
            "Demonstration sentiment model ready  "
            "(vocab=%d, samples=%d)", vocab_size, len(texts),
        )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the sentiment of ``input_data["text"]``.

        Returns:
            ``{"label": str, "confidence": float, "model_type": str}``

        Raises:
            RuntimeError: Model not loaded.
            ValueError:   Invalid input.
        """
        if not self.is_loaded or self._pipeline is None:
            raise RuntimeError("Model is not loaded. Call load() first.")

        # ── validate input ───────────────────────────────────────────
        text = input_data.get("text")
        if text is None:
            raise ValueError("Missing required field: 'text'")
        if not isinstance(text, str):
            raise ValueError(
                f"Field 'text' must be a string, got {type(text).__name__}"
            )
        if not text.strip():
            raise ValueError("Field 'text' must not be empty or whitespace-only")

        # ── inference ────────────────────────────────────────────────
        probabilities = self._pipeline.predict_proba([text])[0]
        predicted_idx = int(np.argmax(probabilities))
        label: str = self._pipeline.classes_[predicted_idx]
        confidence: float = float(probabilities[predicted_idx])

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "model_type": "demonstration",
        }

    def input_contract(self) -> ModelContract:
        return ModelContract(fields={
            "text": FieldContract(
                type="str",
                required=True,
                description="Text to classify for sentiment (English only).",
            ),
        })

    def output_contract(self) -> ModelContract:
        return ModelContract(fields={
            "label": FieldContract(
                type="str",
                required=True,
                description=(
                    "Predicted sentiment label: 'positive' or 'negative'."
                ),
            ),
            "confidence": FieldContract(
                type="float",
                required=True,
                description=(
                    "Model probability estimate for the predicted label. "
                    "NOT a calibrated probability.  Range: [0.0, 1.0]."
                ),
            ),
            "model_type": FieldContract(
                type="str",
                required=True,
                description=(
                    "Always 'demonstration'.  Indicates this is not a "
                    "production model."
                ),
            ),
        })

    def name(self) -> str:
        return "demo_sentiment_classifier"

    def description(self) -> str:
        return (
            "Demonstration sentiment classifier.  Predicts whether input "
            "text expresses positive or negative sentiment.  Trained on a "
            "small built-in dataset (~40 examples).  Not suitable for "
            "production use."
        )

