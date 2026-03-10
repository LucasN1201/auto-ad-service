"""Pydantic schemas for API."""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class CarResponse(BaseModel):
    id: int
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[Decimal] = None
    color: Optional[str] = None
    link: str

    class Config:
        from_attributes = True
