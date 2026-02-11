from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String


class Carbon_metrics(Base):
    __tablename__ = "carbon_metrics"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    learning_path_id = Column(Integer, nullable=True)
    session_duration = Column(Integer, nullable=False)
    carbon_footprint = Column(Float, nullable=False)
    device_type = Column(String(50), nullable=True, default='laptop')
    energy_consumed = Column(Float, nullable=True)
    trees_contribution = Column(Float, nullable=True)
    session_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)