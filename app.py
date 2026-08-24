from fastapi import FastAPI
import joblib
import os
import pandas as pd
import pymysql 
from datetime import datetime
app = FastAPI()
model = joblib.load("mymodel.pkl")
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "ml_db")
}
def get_db_connection():
    return pymysql.connect(**MYSQL_CONFIG)
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            study_hours FLOAT,
            prediction INT,
            status VARCHAR(10),
            created_at DATETIME
        )
    """)
    connection.commit()
    connection.close()
init_db()
@app.get("/")
def testing():
    return {"test": "all okay"}
@app.post("/prediction")
def myprediction(hours: float):
    newdata = pd.DataFrame({"StudyHours": [hours]})
    mynewdata = model.predict(newdata)
    
    pred_val = int(mynewdata[0])
    status_val = "PASS" if pred_val == 1 else "FAIL"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO predictions (study_hours, prediction, status, created_at) VALUES (%s, %s, %s, %s)",
        (hours, pred_val, status_val, current_time)
    )
    connection.commit()
    connection.close()

    return {
        "study_hours": hours,
        "prediction": pred_val,
        "status": status_val,
        "message": "Data successfully saved in MySQL database!"
    }
@app.get("/history")
def get_all_predictions():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    connection.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "study_hours": row[1],
            "prediction": row[2],
            "status": row[3],
            "created_at": row[4]
        })
    return {"history": history}