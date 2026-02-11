import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from core.config import settings

logger = logging.getLogger(__name__)

# JWT Configuration - Use settings from core/config
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ecolearn-secret-key-change-in-production-2024")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = 24


def utcnow_naive():
    """Return current UTC time without timezone info for PostgreSQL compatibility"""
    return datetime.utcnow()


class AuthLocalService:
    """Service for local authentication with email/password and JWT"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user_id: int, email: str, name: Optional[str] = None, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token compatible with core/auth.py"""
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "name": name,
            "role": "user",
            "exp": expire,
            "iat": now,
            "nbf": now,
            "last_login": now.isoformat()
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def register(self, email: str, password: str, name: Optional[str] = None) -> User:
        """Register a new user with email/password"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Un compte avec cet email existe déjà")
        
        # Create new user with offset-naive datetime for PostgreSQL compatibility
        user = User(
            email=email,
            password_hash=self.hash_password(password),
            name=name or email.split('@')[0],
            is_active=True,
            is_verified=True,  # Auto-verify for simplicity
            created_at=utcnow_naive()
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def login(self, email: str, password: str) -> tuple[User, str]:
        """Login with email/password and return user with token"""
        user = await self.get_user_by_email(email)
        
        if not user:
            raise ValueError("Email ou mot de passe incorrect")
        
        if not user.password_hash:
            raise ValueError("Ce compte n'a pas de mot de passe configuré")
        
        if not self.verify_password(password, user.password_hash):
            raise ValueError("Email ou mot de passe incorrect")
        
        if not user.is_active:
            raise ValueError("Ce compte a été désactivé")
        
        # Update last login with offset-naive datetime for PostgreSQL compatibility
        user.last_login = utcnow_naive()
        user.updated_at = utcnow_naive()
        await self.db.commit()
        
        # Create token with user name
        token = self.create_access_token(user.id, user.email, user.name)
        
        return user, token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = self.decode_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        return await self.get_user_by_id(user_id)