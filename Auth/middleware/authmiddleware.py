from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from auth import verify_jwt_token
from shared.logger import getLogger
logger = getLogger("auth-service")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path in ["/login","/register"]:
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
             logger.error("Authorisation header missing")
             return JSONResponse(
             status_code=401,
             content={"detail": "Authorization header missing or malformed"},
             )
        token = auth_header.split(" ")[1]
        try:
            payload = verify_jwt_token(token)
            request.state.user = payload
        except Exception as e:
            return JSONResponse(
            status_code=401,
            content={"detail": str(e)},
        )
        response = await call_next(request)
        return response