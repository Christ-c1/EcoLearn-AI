from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer


class User_stats(Base):
    __tablename__ = "user_stats"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    total_learning_time = Column(Integer, nullable=True, default=0)
    total_carbon_footprint = Column(Float, nullable=True, default=0)
    total_trees_planted = Column(Integer, nullable=True, default=0)
    total_carbon_offset = Column(Float, nullable=True, default=0)
    paths_completed = Column(Integer, nullable=True, default=0)
    current_streak = Column(Integer, nullable=True, default=0)
    longest_streak = Column(Integer, nullable=True, default=0)
    level = Column(Integer, nullable=True, default=1)
    experience_points = Column(Integer, nullable=True, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=True)