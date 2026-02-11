from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String, Text


class Learning_paths(Base):
    __tablename__ = "learning_paths"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String(255), nullable=True)
    difficulty = Column(String(50), nullable=True, default='beginner')
    content = Column(Text, nullable=True)
    progress = Column(Integer, nullable=True, default=0)
    total_sessions = Column(Integer, nullable=True, default=0)
    completed_sessions = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)