"""Model bootstrapping and pre-registration utilities.

Pre-loads production scikit-learn models, the remote REST microservice adapter,
and demonstration fallbacks into the ToolRegistry.
"""

from __future__ import annotations

import logging
from pathlib import Path

from modular_agent.ingestion.engine import IngestionEngine, ModelConfig
from modular_agent.models.registry import ToolRegistry
from modular_agent.models.rest_api_model import default_fraud_evaluator

logger = logging.getLogger(__name__)


def bootstrap_default_models(registry: ToolRegistry) -> None:
    """Pre-ingest all available models into the given registry."""
    engine = IngestionEngine(registry)
    project_root = Path(__file__).resolve().parent.parent.parent.parent

    # 1. Real Scikit-learn Sentiment Pipeline (.joblib)
    real_sentiment_file = project_root / "models" / "artifacts" / "real_sentiment_pipeline.joblib"
    if real_sentiment_file.exists() and not registry.has("real_sentiment_pipeline"):
        res = engine.ingest(
            ModelConfig(
                model_type="sklearn",
                name="real_sentiment_pipeline",
                description="Production scikit-learn TF-IDF + Logistic Regression text sentiment classifier.",
                parameters={"model_path": str(real_sentiment_file)},
            )
        )
        if res.success:
            logger.info("Bootstrap: Ingested 'real_sentiment_pipeline'.")

    # 2. Real Scikit-learn Risk Classifier (.joblib)
    real_risk_file = project_root / "models" / "artifacts" / "real_risk_classifier.joblib"
    if real_risk_file.exists() and not registry.has("real_risk_classifier"):
        res = engine.ingest(
            ModelConfig(
                model_type="sklearn",
                name="real_risk_classifier",
                description="Production Random Forest classifier evaluating risk diagnostic metrics.",
                parameters={"model_path": str(real_risk_file)},
            )
        )
        if res.success:
            logger.info("Bootstrap: Ingested 'real_risk_classifier'.")

    # 3. Real Remote REST Microservice
    if not registry.has("remote_transaction_evaluator"):
        res = engine.ingest(
            ModelConfig(
                model_type="rest_api",
                name="remote_transaction_evaluator",
                description="Remote REST API fraud / transaction risk assessment microservice on port 8001.",
                parameters={
                    "endpoint_url": "http://127.0.0.1:8001/predict",
                    "http_method": "POST",
                    "fallback_handler": default_fraud_evaluator,
                    "input_contract": {
                        "transaction_id": {
                            "type": "str",
                            "required": False,
                            "default": "TX-8041",
                            "description": "Unique transaction ID to evaluate",
                        },
                        "amount": {
                            "type": "float",
                            "required": True,
                            "description": "Transaction monetary amount",
                        },
                        "user_country": {
                            "type": "str",
                            "required": False,
                            "default": "US",
                            "description": "Country code of origin (e.g. 'US', 'DE', 'GB')",
                        },
                        "country": {
                            "type": "str",
                            "required": False,
                            "default": "US",
                            "description": "Alias for user country",
                        },
                    },
                    "output_contract": {
                        "prediction": {
                            "type": "str",
                            "required": True,
                            "description": "Risk assessment: 'approved', 'flagged_for_review', 'declined'",
                        },
                        "risk_score": {
                            "type": "float",
                            "required": True,
                            "description": "Calculated fraud probability score (0.0 to 1.0)",
                        },
                        "model_type": {
                            "type": "str",
                            "required": True,
                            "description": "Service runtime format ('remote_rest_api')",
                        },
                    },
                },
            )
        )
        if res.success:
            logger.info("Bootstrap: Ingested 'remote_transaction_evaluator'.")

    # 4. Demonstration Sentiment Classifier (Fallback)
    if not registry.has("demo_sentiment_classifier"):
        res = engine.ingest(
            ModelConfig(
                model_type="demo",
                name="demo_sentiment_classifier",
                description="Built-in demonstration binary sentiment classifier (TF-IDF + LogisticRegression).",
            )
        )
        if res.success:
            logger.info("Bootstrap: Ingested 'demo_sentiment_classifier'.")

