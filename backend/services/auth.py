import logging
import os
from datetime import datetime
from typing import Optional

from core.database import db_manager
from models.users import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AuthService:
    """Simplified auth service for local authentication"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def initialize_admin_user():
    """Initialize admin user if not exists - simplified for local auth"""
    if "MGX_IGNORE_INIT_ADMIN" in os.environ:
        logger.info("Ignore initialize admin")
        return

    from services.database import initialize_database

    # Ensure database is initialized first
    await initialize_database()

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@ecolearn.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

    if not admin_email:
        logger.warning("Admin email not configured, skipping admin initialization")
        return

    async with db_manager.async_session_maker() as db:
        # Check if admin user already exists
        result = await db.execute(select(User).where(User.email == admin_email))
        user = result.scalar_one_or_none()

        if user:
            logger.debug(f"Admin user {admin_email} already exists")
        else:
            # Create new admin user with hashed password
            import bcrypt
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
            
            admin_user = User(
                email=admin_email,
                password_hash=password_hash,
                name="Admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            await db.commit()
            logger.info(f"Created admin user: {admin_email}")