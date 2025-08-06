import psycopg2
from psycopg2.extras import RealDictCursor
import os
from shared.config import get_env_variable



def connect_db():
    """
    Connects to the PostgreSQL database using the DATABASE_URL from environment variables.
    """
    DATABASE_URL,_,_ = get_env_variable()
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment variables.")
    print(f"Connecting to database at {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def get_user_by_username(email: str):
    DATABASE_URL,_,_ = get_env_variable()
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


