"""Generate real Scikit-learn model artifacts for manual ingestion demonstration.

Produces 3 distinct real models:
1. real_house_price_estimator.joblib (Real Estate Regression)
2. real_loan_approval_predictor.joblib (FinTech Classification)
3. real_student_performance_predictor.joblib (EdTech Classification)
"""

from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def train_house_price_model(out_path: Path):
    """Real Estate Property Valuation Regression Model."""
    np.random.seed(42)
    n = 1000
    sqft = np.random.uniform(600, 4500, n)
    bedrooms = np.random.randint(1, 6, n)
    bathrooms = np.random.randint(1, 5, n)
    location_score = np.random.uniform(1.0, 10.0, n)

    # Realistic price formula with random variance
    prices = (
        60000.0
        + (sqft * 195.0)
        + (bedrooms * 18000.0)
        + (bathrooms * 22000.0)
        + (location_score * 28000.0)
        + np.random.normal(0, 15000, n)
    )

    X = np.column_stack([sqft, bedrooms, bathrooms, location_score])
    y = np.round(prices, -2)

    model = RandomForestRegressor(n_estimators=40, random_state=42)
    model.fit(X, y)
    joblib.dump(model, out_path)
    print(f"[OK] Generated Real Estate Model: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


def train_loan_approval_model(out_path: Path):
    """FinTech Loan Eligibility & Credit Risk Classification Model."""
    np.random.seed(42)
    n = 1000
    monthly_income = np.random.uniform(2500, 25000, n)
    credit_score = np.random.randint(520, 850, n)
    loan_amount = np.random.uniform(20000, 600000, n)
    debt_to_income = np.random.uniform(0.10, 0.65, n)

    # Underwriting scoring rule
    score = (
        (credit_score - 600) * 0.4
        + (monthly_income / 1000.0) * 15.0
        - (debt_to_income * 100.0) * 1.5
        - (loan_amount / 50000.0) * 5.0
    )
    y = (score > 15.0).astype(int)  # 1 = approved, 0 = declined

    X = np.column_stack([monthly_income, credit_score, loan_amount, debt_to_income])
    model = RandomForestClassifier(n_estimators=40, random_state=42)
    model.fit(X, y)
    joblib.dump(model, out_path)
    print(f"[OK] Generated Loan Approval Model: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


def train_student_performance_model(out_path: Path):
    """EdTech Student Exam Pass / Fail Prediction Model."""
    np.random.seed(42)
    n = 1000
    study_hours = np.random.uniform(2.0, 45.0, n)
    attendance_rate = np.random.uniform(45.0, 100.0, n)
    previous_grade = np.random.uniform(40.0, 100.0, n)

    score = (study_hours * 1.8) + (attendance_rate * 0.4) + (previous_grade * 0.5)
    y = (score >= 80.0).astype(int)  # 1 = pass, 0 = fail

    X = np.column_stack([study_hours, attendance_rate, previous_grade])
    model = RandomForestClassifier(n_estimators=40, random_state=42)
    model.fit(X, y)
    joblib.dump(model, out_path)
    print(f"[OK] Generated Student Performance Model: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    artifacts_dir = Path(__file__).resolve().parent.parent / "models" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    train_house_price_model(artifacts_dir / "real_house_price_estimator.joblib")
    train_loan_approval_model(artifacts_dir / "real_loan_approval_predictor.joblib")
    train_student_performance_model(artifacts_dir / "real_student_performance_predictor.joblib")
