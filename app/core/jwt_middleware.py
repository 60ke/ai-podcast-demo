from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.config import settings

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 排除OPTIONS请求和generate_script接口
        if request.method == "OPTIONS" or request.url.path.endswith("/generate_script"):
            return await call_next(request)
        
        if request.url.path.startswith("/podcast"):  # 仅对/podcast接口鉴权
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"detail": "未提供有效的JWT Token"})
            token = auth_header.split(" ", 1)[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                request.state.user_id = payload.get("user_id")
                if not request.state.user_id:
                    return JSONResponse(status_code=401, content={"detail": "Token无用户信息"})
            except ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token已过期"})
            except InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "无效的Token"})
        return await call_next(request) 