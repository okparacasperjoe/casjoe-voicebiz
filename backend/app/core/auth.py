"""
JWT authentication middleware.
Validates Casjoe Biz JWT tokens and extracts user_id + business_id.
The business_id from the token is authoritative — never trust client-supplied values.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from uuid import UUID
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    user_id: str
    business_id: str
    exp: int | None = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> TokenPayload:
    """
    FastAPI dependency.
    Validates the Bearer token and returns the decoded payload.
    Raises 401 if the token is invalid or expired.
    """
    if not credentials:
        if settings.APP_ENV == "development":
            return TokenPayload(
                user_id="dev-user-id",
                business_id="dev-business-id"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    try:
        # In dev mode, if the token is literal 'mock_token', allow it
        if settings.APP_ENV == "development" and token == "mock_token":
             return TokenPayload(user_id="dev-user", business_id="dev-business")
             
        payload = jwt.decode(
            token,
            settings.CASJOE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )
        user_id = payload.get("user_id") or payload.get("sub")
        business_id = payload.get("business_id")

        if not user_id or not business_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing required fields: user_id, business_id",
            )

        return TokenPayload(user_id=user_id, business_id=business_id)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
