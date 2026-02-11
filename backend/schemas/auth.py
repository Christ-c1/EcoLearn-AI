from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: Union[str, int]  # Support both string (OIDC) and int (local auth)
    email: str
    name: Optional[str] = None
    role: str = "user"  # user/admin
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlatformTokenExchangeRequest(BaseModel):
    """Request body for exchanging Platform token for app token."""

    platform_token: str


class TokenExchangeResponse(BaseModel):
    """Response body for issued application token."""

    token: str