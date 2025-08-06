from fastapi import FastAPI, HTTPException
from pydantic import BaseModel



from shared.logger import getLogger
from db import get_user_by_username
from passlib.context import CryptContext
from auth_utils import create_jwt_token
import grpc
import os
import sys
from fastapi.responses import JSONResponse
from google.protobuf import empty_pb2
from fastapi import status
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Logs_Generator.LogsGen import logs_pb2, logs_pb2_grpc 
logger = getLogger("auth-service")

app = FastAPI() 

class User(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(credentials: User):
    """
    Endpoint to handle user login.  
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    logger.info(f"Login attempt for user: {credentials.email}")
    user = get_user_by_username(credentials.email)
    if not user or not pwd_context.verify(credentials.password, user["password"]):
        logger.error(f"Login failed for user: {credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    logger.info(f"Login successful for user: {credentials.email}")
    created_token = create_jwt_token({"email": credentials.email})
    try:
            with grpc.insecure_channel("logservice:5000") as channel:
                stub = logs_pb2_grpc.LogsServiceStub(channel)
                stub.logs(empty_pb2.Empty())
                logger.info("Triggered log generation via gRPC.")
    except grpc.RpcError as grpc_error:
            logger.error(f"gRPC log service failed: {grpc_error}")

    return JSONResponse(
            content={"access_token": created_token, "token_type": "bearer"},
            status_code=status.HTTP_201_CREATED
        )
    