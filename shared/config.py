import os
from dotenv import load_dotenv
from pathlib import Path



def get_env_variable():
    # Always load from root .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    ALGORTHIM = os.getenv("ALGORITHM")
    if not DATABASE_URL or not JWT_SECRET or not ALGORTHIM:
        raise ValueError("One or more environment variables are not set.")
    return DATABASE_URL, JWT_SECRET, ALGORTHIM