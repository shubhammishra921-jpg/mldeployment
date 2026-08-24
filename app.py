import os
import pymysql
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. Load Model
model = joblib.load("mymodel.pkl")

# 2. Schema (Exact match with training feature)
class InputData(BaseModel):
    StudyHours: float

# 3. Database Connection
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

@app.get("/")
def home():
    return {"message": "Database Connected & API is Live!"}

@app.post("/predict")
def predict(data: InputData):
    try:
        # Pydantic to DataFrame
        input_dict = data.model_dump() if hasattr(data, "model_dump") else data.dict()
        input_df = pd.DataFrame([input_dict])
        
        # Prediction
        prediction = model.predict(input_df)
        result = float(prediction[0])

        # Save to DB (optional/safe check)
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "INSERT INTO predictions (prediction_value) VALUES (%s)"
                cursor.execute(sql, (result,))
                conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"DB Insert Error: {db_err}")

        return {"status": "success", "prediction": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction Error: {str(e)}")