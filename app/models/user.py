from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    attributes = Column(JSON, default={})  # For ABAC later
    created_at = Column(DateTime(timezone=True), server_default=func.now())
