"""API routes: login and cars."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import verify_password, create_access_token
from app.database import get_db
from app.models import User, Car
from app.schemas import Token, LoginRequest, CarResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Authorize and return JWT."""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return Token(access_token=create_access_token(user.username))


@router.get("/cars", response_model=list[CarResponse])
def list_cars(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Secure list of cars (requires valid JWT)."""
    cars = db.query(Car).order_by(Car.updated_at.desc()).all()
    return [CarResponse.model_validate(c) for c in cars]
