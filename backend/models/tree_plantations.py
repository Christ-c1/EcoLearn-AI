from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String


class Tree_plantations(Base):
    __tablename__ = "tree_plantations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    trees_planted = Column(Integer, nullable=False)
    carbon_offset = Column(Float, nullable=False)
    location = Column(String(255), nullable=True)
    tree_species = Column(String(255), nullable=True)
    plantation_date = Column(DateTime(timezone=True), nullable=True)
    certificate_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)