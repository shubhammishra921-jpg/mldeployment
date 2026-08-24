import os
import pymysql
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# 1. FastAPI App Initialize
app = FastAPI()

# 2. ML Model Load
model = joblib.load("mymodel.pkl")

# 3. Input Data Schema
class InputData(BaseModel):
    Name: str
    Age: int
    Address: str

# 4. Database Connection Setup
DB_HOST = os.getenv('Host', '').strip()
DB_USER = os.getenv('User', '').strip()
DB_PASSWORD = os.getenv('Password', '').strip()
DB_NAME = os.getenv('Database_name', '').strip()
DB_PORT = os.getenv('Port', '27728').strip()

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT),
        ssl={'ssl': {}}
    )

# 5. Home Route
@app.get("/")
def home():
    return {"message": "Database Connected & API is Live!"}

# 6. ML Prediction Endpoint
@app.post("/predict")
def predict(data: InputData):
    # Pydantic dict conversion (v2 support)
    input_dict = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    input_df = pd.DataFrame([input_dict])
    
    # Model Prediction
    prediction = model.predict(input_df)
    result = float(prediction[0])
    
    # Save Prediction to DB
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO predictions (prediction_value) VALUES (%s)"
            cursor.execute(sql, (result,))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Insert Error: {e}")

    return {"prediction": result}