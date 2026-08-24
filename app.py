import os
import pymysql

# 1. Render Environment Variables (Case-sensitive!)
DB_HOST = os.getenv('Host')
DB_USER = os.getenv('User')
DB_PASSWORD = os.getenv('Password')
DB_NAME = os.getenv('Database_name')
DB_PORT = os.getenv('Port')

# 2. Debug Log: Ye Render log mein print hoga taaki check kar sakein ki value aa rahi hai ya nahi
print(f"--- DB CONNECTING TO: {DB_HOST} ON PORT: {DB_PORT} ---")

# 3. MySQL Connection Block
try:
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT) if DB_PORT else 27728,  # Port integer hona zaroori hai
        ssl={'ssl': {}}  # Aiven database ke liye SSL mandatory hai
    )
    print("--- DB CONNECTION SUCCESSFUL! ---")
except Exception as e:
    print(f"--- DB CONNECTION FAILED: {e} ---")
    raise e