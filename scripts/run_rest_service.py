"""Real REST API Inference Microservice.

Runs an independent HTTP REST model endpoint on port 8001 to demonstrate
real remote REST model ingestion and execution with Modular-Agent.

Run with:
    python scripts/run_rest_service.py
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(
    title="Real Remote Fraud / Risk Scoring Microservice",
    description="Independent production-style REST inference microservice.",
    version="1.0.0",
)


class TransactionRequest(BaseModel):
    transaction_id: str = Field(default="TX-DEFAULT", description="Unique transaction ID to evaluate.")
    amount: float = Field(default=100.0, description="Transaction monetary amount.")
    user_country: Optional[str] = Field(default=None, description="Country code of origin.")
    country: Optional[str] = Field(default=None, description="Alias for user_country.")


class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Risk assessment: 'approved', 'flagged_for_review', 'declined'.")
    risk_score: float = Field(..., description="Calculated fraud probability score (0.0 to 1.0).")
    model_type: str = Field(default="remote_rest_api", description="Service runtime format.")


def evaluate_transaction_logic(data: dict) -> dict:
    """Core deterministic fraud / risk assessment algorithm."""
    amount = float(data.get("amount", 100.0))
    country = str(data.get("user_country") or data.get("country") or "US").upper()

    score = 0.05
    if amount > 10000.0:
        score += 0.65
    elif amount > 2000.0:
        score += 0.30

    if country not in ("US", "CA", "GB", "DE", "IN"):
        score += 0.25

    score = min(score, 0.99)

    if score >= 0.70:
        decision = "declined"
    elif score >= 0.35:
        decision = "flagged_for_review"
    else:
        decision = "approved"

    return {
        "prediction": decision,
        "risk_score": round(score, 4),
        "model_type": "remote_rest_api",
    }


@app.post("/predict", response_model=PredictionResponse)
def evaluate_transaction(req: TransactionRequest):
    """Real deterministic fraud / risk assessment algorithm."""
    res = evaluate_transaction_logic(req.model_dump())
    return PredictionResponse(**res)


@app.get("/health")
def health():
    return {"status": "online", "service": "fraud_detection_api"}


if __name__ == "__main__":
    print("Starting real remote REST inference microservice on http://127.0.0.1:8001 ...")
    uvicorn.run(app, host="127.0.0.1", port=8001)

