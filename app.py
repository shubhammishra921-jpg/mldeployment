import os
import pymysql
from fastapi import FastAPI

# 1. FastAPI App Initialize Karo (Ye line Uvicorn ke liye zaroori hai!)
app = FastAPI()

# 2. Database Connection Logic (Aapka working code)
DB_HOST = os.getenv('Host', '').strip()
DB_USER = os.getenv('User', '').strip()
DB_PASSWORD = os.getenv('Password', '').strip()
DB_NAME = os.getenv('Database_name', '').strip()
DB_PORT = os.getenv('Port', '27728').strip()

print(f"--- DB CONNECTING TO: {DB_HOST} ON PORT: {DB_PORT} AS USER: {DB_USER} ---")

try:
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT),
        ssl={'ssl': {}}
    )
    print("--- DB CONNECTION SUCCESSFUL! ---")
except Exception as e:
    print(f"--- DB CONNECTION FAILED: {e} ---")
    raise e

# 3. Simple Test Route
@app.get("/")
def home():
    return {"message": "Database Connected & API is Live!"}