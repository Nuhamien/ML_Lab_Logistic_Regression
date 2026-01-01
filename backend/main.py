import os
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

# 1. REMOVED MANGUM: This fixes the 'issubclass' TypeError
# Vercel handles the 'app' object directly.

# 2. Robust Path Loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(filename):
    return os.path.join(BASE_DIR, filename)

# Load Logistic Model and Scaler
try:
    # Use global variables so they stay in memory across requests
    model = joblib.load(get_model_path("loan_lr_model.joblib"))
    scaler = joblib.load(get_model_path("loan_scaler.joblib"))
    print("Successfully loaded Logistic Regression assets.")
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    scaler = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoanInput(BaseModel):
    gender: int
    married: int
    dependents: int
    education: int
    self_employed: int
    applicant_income: float
    coapplicant_income: float
    loan_amount: float
    loan_term: float
    credit_history: float
    property_area: int

@app.post("/predict")
def predict_loan(data: LoanInput):
    if model is None or scaler is None:
        return {"error": "Model not loaded on server"}, 500

    features = [
        data.gender, data.married, data.dependents, data.education,
        data.self_employed, data.applicant_income, data.coapplicant_income,
        data.loan_amount, data.loan_term, data.credit_history, data.property_area
    ]
    
    # Logistic Regression MUST use scaled data
    features_array = np.array([features])
    scaled_features = scaler.transform(features_array)
    prediction = model.predict(scaled_features)

    result = "Approved" if prediction[0] == 1 else "Rejected"
    return {"status": result, "model_used": "Logistic Regression"}

@app.get("/")
def home():
    return {"message": "Logistic Regression API is Live!"}