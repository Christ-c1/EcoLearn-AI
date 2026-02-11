import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.auth_local import AuthLocalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None


class TokenVerifyRequest(BaseModel):
    token: str


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user with email and password"""
    try:
        auth_service = AuthLocalService(db)
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        token = auth_service.create_access_token(user.id, user.email)
        
        return AuthResponse(
            success=True,
            message="Inscription réussie!",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified
            ),
            token=token
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription")


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    try:
        auth_service = AuthLocalService(db)
        user, token = await auth_service.login(
            email=request.email,
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            message="Connexion réussie!",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified
            ),
            token=token
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")


@router.post("/verify-token", response_model=AuthResponse)
async def verify_token(
    request: TokenVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify a JWT token and return user info"""
    try:
        auth_service = AuthLocalService(db)
        user = await auth_service.get_current_user(request.token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré")
        
        return AuthResponse(
            success=True,
            message="Token valide",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified
            ),
            token=request.token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de vérification")


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"success": True, "message": "Déconnexion réussie"}