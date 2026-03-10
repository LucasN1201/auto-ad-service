"""Database connection and car queries for the bot."""
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    make = Column(String(128))
    model = Column(String(256))
    year = Column(Integer)
    price = Column(Numeric(12, 2))
    color = Column(String(64))
    link = Column(String(512))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def query_cars(
    make: str | None = None,
    model: str | None = None,
    color: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    price_max: int | None = None,
    price_min: int | None = None,
    limit: int = 20,
) -> list[dict]:
    """Query cars with optional filters. All filters are case-insensitive partial match except numeric ranges."""
    db = Session()
    try:
        q = db.query(Car).filter(Car.link.isnot(None))
        if make:
            q = q.filter(Car.make.ilike(f"%{make}%"))
        if model:
            q = q.filter(Car.model.ilike(f"%{model}%"))
        if color:
            q = q.filter(Car.color.ilike(f"%{color}%"))
        if year_min is not None:
            q = q.filter(Car.year >= year_min)
        if year_max is not None:
            q = q.filter(Car.year <= year_max)
        if price_max is not None:
            q = q.filter(Car.price <= price_max)
        if price_min is not None:
            q = q.filter(Car.price >= price_min)
        rows = q.order_by(Car.id.desc()).limit(limit).all()
        return [
            {
                "make": r.make,
                "model": r.model,
                "year": r.year,
                "price": float(r.price) if r.price is not None else None,
                "color": r.color,
                "link": r.link,
            }
            for r in rows
        ]
    finally:
        db.close()
