import os
import pymysql
import joblib
import pandas as pd
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="ML Score Predictor")

# 1. Load Model
model = joblib.load("mymodel.pkl")

# 2. Database Connection
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

class InputData(BaseModel):
    StudyHours: float

# 3. HTML Frontend Route
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ML Pass/Fail Predictor</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 360px; text-align: center; }
            h2 { color: #333; margin-bottom: 20px; font-size: 22px; }
            input[type="number"] { width: 90%; padding: 12px; margin: 10px 0 20px 0; border: 1px solid #ccc; border-radius: 6px; font-size: 16px; outline: none; }
            input[type="number"]:focus { border-color: #4CAF50; }
            button { background-color: #4CAF50; color: white; padding: 12px; border: none; border-radius: 6px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.3s; }
            button:hover { background-color: #45a049; }
            .result { margin-top: 20px; font-size: 18px; padding: 12px; border-radius: 6px; display: none; font-weight: bold; }
            .pass-badge { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .fail-badge { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Study Hours Predictor</h2>
            <form id="predictForm">
                <input type="number" id="studyHours" step="0.1" min="0" max="24" placeholder="Enter Study Hours (e.g. 5.5)" required>
                <button type="submit">Predict Result</button>
            </form>
            <div id="resultBox" class="result"></div>
        </div>

        <script>
            document.getElementById('predictForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const hours = parseFloat(document.getElementById('studyHours').value);
                const resultBox = document.getElementById('resultBox');
                
                resultBox.style.display = 'block';
                resultBox.className = 'result';
                resultBox.style.backgroundColor = '#e2e3e5';
                resultBox.style.color = '#383d41';
                resultBox.innerText = 'Predicting...';
                
                try {
                    const response = await fetch('/predict-web', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `StudyHours=${hours}`
                    });
                    const data = await response.json();
                    if(data.status === 'success') {
                        // PASS / FAIL display logic
                        if (data.status_text === 'PASS') {
                            resultBox.className = 'result pass-badge';
                            resultBox.innerText = `Result: PASS 🎉`;
                        } else {
                            resultBox.className = 'result fail-badge';
                            resultBox.innerText = `Result: FAIL ❌`;
                        }
                    } else {
                        resultBox.className = 'result fail-badge';
                        resultBox.innerText = 'Error making prediction';
                    }
                } catch (err) {
                    resultBox.className = 'result fail-badge';
                    resultBox.innerText = 'Server Error!';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 4. Web Endpoint
@app.post("/predict-web")
def predict_web(StudyHours: float = Form(...)):
    try:
        input_df = pd.DataFrame([{"StudyHours": StudyHours}])
        prediction = model.predict(input_df)
        raw_val = float(prediction[0])

        # 0 ko FAIL aur 1 (ya >0) ko PASS map karte hain
        status_text = "PASS" if raw_val >= 1.0 else "FAIL"

        # Save to DB
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "INSERT INTO predictions (prediction_value) VALUES (%s)"
                cursor.execute(sql, (raw_val,))
                conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"DB Insert Error: {db_err}")

        return {
            "status": "success", 
            "prediction": raw_val,
            "status_text": status_text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 5. JSON Endpoint (Swagger Docs)
@app.post("/predict")
def predict(data: InputData):
    try:
        input_df = pd.DataFrame([{"StudyHours": data.StudyHours}])
        prediction = model.predict(input_df)
        raw_val = float(prediction[0])
        status_text = "PASS" if raw_val >= 1.0 else "FAIL"

        return {
            "status": "success", 
            "prediction": raw_val,
            "status_text": status_text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))