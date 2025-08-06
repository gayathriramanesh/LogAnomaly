from fastapi import FastAPI
from shared.logger import getLogger
import os
from jose import JWTError, jwt
from fastapi import HTTPException, status
from datetime import datetime
from passlib.context import CryptContext
from db import connect_db
from contextlib import asynccontextmanager

logger= getLogger("auth-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes the database by creating the necessary tables.
    """
    logger = getLogger("auth-service")
    conn = connect_db()
    cur = conn.cursor()
    
    # Create users table if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR PRIMARY KEY,
            password VARCHAR NOT NULL
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    logger.info("Database initialized successfully.")
    yield


app = FastAPI(lifespan=lifespan)

def verify_jwt_token(token:str)->dict:
    """
    Verifies the JWT token using the secret key and algorithm from the environment variables.
    """
    secret_key = os.getenv('JWT_SECRET_KEY')
    algorithm = os.getenv('ALGORITHM')
    if not secret_key or not algorithm:
        logger.error("JWT_SECRET_KEY or ALGORITHM not set in environment variables.")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        exp = payload.get('exp')
        if exp and datetime.utcnow().timestamp() > exp:
            logger.error("Token has expired.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
    except JWTError:
        logger.error("Invalid token.")
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    return payload

def create_jwt_token(data: dict, expires_delta: int = 1000) -> str:
    """
    Creates a JWT token with the given data and expiration time.
    """
    secret_key = os.getenv('JWT_SECRET_KEY')
    algorithm = os.getenv('ALGORITHM')
    if not secret_key or not algorithm:
        logger.error("JWT_SECRET_KEY or ALGORITHM not set in environment variables.")
        return ""
    if not data.get('email'):
        logger.error("Email is required to create a JWT token.")
        return ""
    expire = datetime.utcnow().timestamp() + expires_delta
    payload = {
        'exp': expire,
        'email': data.get('email')
    }
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token

def hash_pwd(password:str):
    """Hashes the password using bcrypt algorithm."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash(password)
    return hashed


def verify_user(email: str, password: str):
    """
    Verifies the user credentials against the database.
    """
    conn = connect_db()
    cur = conn.cursor()
    encrypted_password = hash_pwd(password)
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, encrypted_password))
    user = cur.fetchone()
    if user:
        logger.info(f"User {email} verified successfully.")
    else:
        logger.error(f"User {email} verification failed.")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    cur.close()
    conn.close()

    

    