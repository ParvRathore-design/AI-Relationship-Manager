"""
AI Relationship Manager
FastAPI Backend
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==========================================
# Create FastAPI Application
# ==========================================

app = FastAPI(
    title="AI Relationship Manager API",
    description="AI-powered Customer Churn Prediction and Recommendation System",
    version="1.0.0"
)

# ==========================================
# Enable CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Project Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models"
DATA_PATH = BASE_DIR / "data"
OUTPUT_PATH = BASE_DIR / "outputs"

# ==========================================
# Load Trained Models
# ==========================================

xgboost_model = None
preprocessor = None
shap_explainer = None
feature_names = None

print("Loading models...")

try:
    xgboost_model = joblib.load(MODEL_PATH / "xgboost_model.pkl")
    preprocessor = joblib.load(MODEL_PATH / "preprocessor.pkl")
    shap_explainer = joblib.load(MODEL_PATH / "shap_explainer.pkl")

    # Feature names after preprocessing (needed for SHAP output labels).
    # Requires scikit-learn's ColumnTransformer/Pipeline to support
    # get_feature_names_out(), which sklearn >=1.0 does.
    feature_names = preprocessor.get_feature_names_out()

    print("Models loaded successfully!")

except Exception as e:
    print(f"Error loading models: {e}")


# ==========================================
# Startup Validation
# ==========================================

@app.on_event("startup")
def startup_event():

    if xgboost_model is None:
        raise RuntimeError("XGBoost model could not be loaded.")

    if preprocessor is None:
        raise RuntimeError("Preprocessor could not be loaded.")

    if shap_explainer is None:
        raise RuntimeError("SHAP explainer could not be loaded.")

    print("API Ready")


# ==========================================
# Request Schema
# ==========================================

class CustomerData(BaseModel):

    CustomerID: str

    Gender: str
    Senior_Citizen: str
    Partner: str
    Dependents: str
    Tenure_Months: int
    Phone_Service: str
    Multiple_Lines: str
    Internet_Service: str
    Online_Security: str
    Online_Backup: str
    Device_Protection: str
    Tech_Support: str
    Streaming_TV: str
    Streaming_Movies: str
    Contract: str
    Paperless_Billing: str
    Payment_Method: str
    Monthly_Charges: float
    Total_Charges: float


# ==========================================
# Health Check Endpoints
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Relationship Manager API",
        "documentation": "/docs",
        "health": "/health",
        "prediction": "/predict"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": xgboost_model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "shap_loaded": shap_explainer is not None
    }


@app.get("/info")
def info():
    return {
        "application": "AI Relationship Manager",
        "version": "1.0",
        "model": "XGBoost",
        "explainability": "SHAP",
        "status": "Running"
    }


# ==========================================
# Health Score / Risk / Priority / Revenue helpers
# ==========================================

def calculate_health_score(churn_probability: float) -> int:
    score = int((1 - churn_probability) * 100)
    return max(0, min(score, 100))


def get_risk_level(probability: float) -> str:
    if probability >= 0.80:
        return "Very High"
    elif probability >= 0.60:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    elif probability >= 0.20:
        return "Low"
    return "Very Low"


def revenue_at_risk(monthly_charge: float, probability: float) -> float:
    annual_revenue = monthly_charge * 12
    return round(annual_revenue * probability, 2)


def customer_priority(probability: float) -> str:
    if probability >= 0.80:
        return "Immediate Attention"
    elif probability >= 0.60:
        return "High Priority"
    elif probability >= 0.40:
        return "Medium Priority"
    return "Low Priority"


# ==========================================
# SHAP Explainability
# ==========================================

def get_top_drivers(processed_data, top_n: int = 5):
    """
    processed_data: already-transformed (preprocessor.transform) input,
    reused from the caller so we don't transform twice.
    """
    try:
        shap_values = shap_explainer(processed_data)
        values = np.abs(shap_values.values[0])

        importance = pd.DataFrame({
            "Feature": feature_names,
            "Importance": values
        })

        importance = importance.sort_values(by="Importance", ascending=False)

        return importance.head(top_n)["Feature"].tolist()

    except Exception as e:
        print(f"SHAP explanation failed: {e}")
        return []


# ==========================================
# AI Recommendations
# ==========================================

def generate_recommendations(probability: float):

    if probability >= 0.80:
        return [
            "Offer a retention discount",
            "Assign a dedicated relationship manager",
            "Schedule a proactive customer call",
            "Review contract and service plan"
        ]

    elif probability >= 0.60:
        return [
            "Send personalized retention offers",
            "Provide loyalty rewards",
            "Recommend service upgrades"
        ]

    return [
        "Maintain regular engagement",
        "Share new feature updates",
        "Monitor customer satisfaction"
    ]


# ==========================================
# Executive Summary
# ==========================================

def executive_summary(probability: float) -> str:

    if probability >= 0.80:
        return (
            "Customer shows a very high probability of churn. "
            "Immediate retention efforts are recommended."
        )

    elif probability >= 0.60:
        return (
            "Customer is at elevated churn risk. "
            "Targeted engagement is advised."
        )

    elif probability >= 0.40:
        return (
            "Customer exhibits moderate churn indicators. "
            "Continue monitoring."
        )

    return "Customer appears loyal with a low probability of churn."


# ==========================================
# Prediction Endpoint
# ==========================================

@app.post("/predict")
def predict(customer: CustomerData):

    if xgboost_model is None or preprocessor is None or shap_explainer is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check server logs.")

    try:
        input_df = pd.DataFrame([customer.model_dump()])
        model_input = input_df.drop(columns=["CustomerID"])

        # Transform once, reuse for both prediction and SHAP
        processed_data = preprocessor.transform(model_input)

        prediction = xgboost_model.predict(processed_data)[0]
        probability = float(xgboost_model.predict_proba(processed_data)[0][1])

        top_drivers = get_top_drivers(processed_data)
        recommendations = generate_recommendations(probability)
        summary = executive_summary(probability)
        health_score = calculate_health_score(probability)
        risk = get_risk_level(probability)
        revenue = revenue_at_risk(customer.Monthly_Charges, probability)
        priority = customer_priority(probability)

        return {
            "customer_id": customer.CustomerID,
            "prediction": "Likely to Churn" if prediction == 1 else "Likely to Stay",
            "churn_probability": round(probability, 4),
            "health_score": health_score,
            "risk_level": risk,
            "customer_priority": priority,
            "annual_revenue_at_risk": revenue,
            "top_drivers": top_drivers,
            "recommendations": recommendations,
            "executive_summary": summary
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
