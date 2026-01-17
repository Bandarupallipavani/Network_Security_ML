import sys
import os
import certifi
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

import pandas as pd
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME
)

# -------------------- ENV --------------------
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# -------------------- APP --------------------
app = FastAPI(title="Network Security ML API")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DB (OPTIONAL) --------------------
collection = None
if MONGO_DB_URL:
    try:
        ca = certifi.where()
        client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
        db = client[DATA_INGESTION_DATABASE_NAME]
        collection = db[DATA_INGESTION_COLLECTION_NAME]
        print("✅ MongoDB connected")
    except Exception as e:
        print("⚠️ MongoDB connection failed:", e)
else:
    print("⚠️ MongoDB not configured – running without DB")

# -------------------- ROUTES --------------------
@app.get("/")
def root():
    return RedirectResponse("/docs")

@app.get("/health")
def health():
    return {"status": "running"}

@app.get("/train")
def train():
    try:
        TrainingPipeline().run_pipeline()
        return {"message": "Training completed"}
    except Exception as e:
        raise NetworkSecurityException(e, sys)

@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")

        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=model
        )

        df["prediction"] = network_model.predict(df)
        return templates.TemplateResponse(
            "table.html",
            {"request": request, "table": df.to_html()}
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)
