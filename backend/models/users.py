from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from core.database import Base


def utcnow():
    """Return current UTC time without timezone info for PostgreSQL compatibility"""
    return datetime.utcnow()


class User(Base):
    """User model for local authentication with email/password"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps - using offset-naive datetime for PostgreSQL compatibility
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    last_login = Column(DateTime, nullable=True)