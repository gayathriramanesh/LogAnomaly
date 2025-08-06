from fastapi import FastAPI
from shared.logger import getLogger
from Auth.db import connect_db
from passlib.context import CryptContext
import grpc
import os
import sys
from fastapi.responses import JSONResponse
from google.protobuf import empty_pb2
from fastapi import status
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Logs_Generator.LogsGen import logs_pb2, logs_pb2_grpc  
from pydantic import BaseModel, EmailStr
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = getLogger("registration-service")


app = FastAPI()




class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/register")
def register_new_user(register_payload:RegisterRequest):
    """
    Endpoint to handle user registration.
    """
    logger.info(f"Registration attempt for user: {register_payload.email}")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS USERS (email VARCHAR PRIMARY KEY, password VARCHAR)")
    try:
        #Hash the password before storing it
        hashed_pw = pwd_context.hash(register_payload.password)
        cur.execute("INSERT INTO USERS (email, password) VALUES (%s, %s)", (register_payload.email, hashed_pw))
        print(f"User {register_payload.email} registered successfully.")

        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Registration successful for user: {register_payload.email}")
        try:
            with grpc.insecure_channel("logservice:5000") as channel:
                stub = logs_pb2_grpc.LogsServiceStub(channel)
                stub.logs(empty_pb2.Empty())
                logger.info("Triggered log generation via gRPC.")
        except grpc.RpcError as grpc_error:
            logger.error(f"gRPC log service failed: {grpc_error}")

        return JSONResponse(
            content={"message": "User registered successfully."},
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Registration failed because of {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST
        )
