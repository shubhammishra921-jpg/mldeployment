import os
import pymysql
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# 1. FastAPI App Initialize
app = FastAPI()

# 2. ML Model Load Karo
model = joblib.load("mymodel.pkl")

# 3. Input Data Schema (Apne features ke hisab se fields change kar sakte ho)
from pydantic import BaseModel

# Input schema ko apne actual inputs se match karein
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

# 5. Home Route (Test Route)
@app.get("/")
def home():
    return {"message": "Database Connected & API is Live!"}

# 6. ML Prediction Endpoint
@app.post("/predict")
def predict(data: InputData):
    # Input ko DataFrame me convert karein
    input_df = pd.DataFrame([data.dict()])
    
    # Model se prediction lein
    prediction = model.predict(input_df)
    result = float(prediction[0])
    
    # Optional: Prediction ko Database me save karein
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Apne table name aur column names ke hisab se query update karein:
            sql = "INSERT INTO predictions (prediction_value) VALUES (%s)"
            cursor.execute(sql, (result,))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Insert Error: {e}")

    return {"prediction": result}