"""SQLAlchemy models for cars and users."""
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Admin/user for API login."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Car(Base):
    """Car ad from scraper. Upsert key: link (unique)."""

    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(128), nullable=True, index=True)
    model = Column(String(256), nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=True)
    color = Column(String(64), nullable=True)
    link = Column(String(512), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
