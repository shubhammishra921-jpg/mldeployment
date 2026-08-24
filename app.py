import os
import pymysql
import joblib
import pandas as pd
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

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

# 3. HTML Frontend Route (Home Page)
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Score Predictor</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 350px; text-align: center; }
            h2 { color: #333; margin-bottom: 20px; }
            input[type="number"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
            button { background-color: #4CAF50; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold; }
            button:hover { background-color: #45a049; }
            .result { margin-top: 20px; font-size: 18px; color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px; display: none; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Study Hours Predictor</h2>
            <form id="predictForm">
                <input type="number" id="studyHours" step="0.1" placeholder="Enter Study Hours (e.g. 5.5)" required>
                <button type="submit">Predict Score</button>
            </form>
            <div id="resultBox" class="result"></div>
        </div>

        <script>
            document.getElementById('predictForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const hours = parseFloat(document.getElementById('studyHours').value);
                const resultBox = document.getElementById('resultBox');
                
                resultBox.style.display = 'block';
                resultBox.innerText = 'Predicting...';
                
                try {
                    const response = await fetch('/predict-web', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `StudyHours=${hours}`
                    });
                    const data = await response.json();
                    if(data.status === 'success') {
                        resultBox.innerText = `Predicted Output: ${data.prediction.toFixed(2)}`;
                    } else {
                        resultBox.innerText = 'Error making prediction';
                    }
                } catch (err) {
                    resultBox.innerText = 'Server Error!';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 4. Web Form Submission Route
@app.post("/predict-web")
def predict_web(StudyHours: float = Form(...)):
    try:
        input_df = pd.DataFrame([{"StudyHours": StudyHours}])
        prediction = model.predict(input_df)
        result = float(prediction[0])

        # DB Insertion (Optional)
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
        raise HTTPException(status_code=400, detail=str(e))