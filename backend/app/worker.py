"""
Worker: periodically run scraper and upsert cars into DB.
Upsert: update existing by link, insert new. Run with: python -m app.worker
"""
import logging
import time
import sys
import os

# Ensure backend root is on path for Docker and local
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Car
from app.scraper import run_scrape

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRAPE_INTERVAL_SEC = int(os.environ.get("SCRAPE_INTERVAL_SEC", "300"))  # 5 min default
MAX_LISTINGS = int(os.environ.get("MAX_LISTINGS", "100"))


def upsert_cars(db: Session, cars: list[dict]) -> tuple[int, int]:
    """Insert new cars and update existing (by link). Returns (inserted, updated)."""
    inserted, updated = 0, 0
    for d in cars:
        link = d.get("link")
        if not link:
            continue
        existing = db.query(Car).filter(Car.link == link).first()
        if existing:
            existing.make = d.get("make")
            existing.model = d.get("model")
            existing.year = d.get("year")
            existing.price = d.get("price")
            if d.get("color") is not None:
                existing.color = d.get("color")
            updated += 1
        else:
            db.add(Car(
                make=d.get("make"),
                model=d.get("model"),
                year=d.get("year"),
                price=d.get("price"),
                color=d.get("color"),
                link=link,
            ))
            inserted += 1
    db.commit()
    return inserted, updated


def run_once() -> None:
    db = SessionLocal()
    try:
        logger.info("Starting scrape (max_listings=%s)...", MAX_LISTINGS)
        cars = run_scrape(max_listings=MAX_LISTINGS, fetch_colors=False)
        logger.info("Scraped %s listings", len(cars))
        if cars:
            ins, upd = upsert_cars(db, cars)
            logger.info("Upsert: inserted=%s updated=%s", ins, upd)
    except Exception as e:
        logger.exception("Scrape/upsert failed: %s", e)
        db.rollback()
    finally:
        db.close()


def main() -> None:
    logger.info("Worker started (interval=%ss)", SCRAPE_INTERVAL_SEC)
    while True:
        try:
            run_once()
        except Exception as e:
            logger.exception("Worker run failed: %s", e)
        time.sleep(SCRAPE_INTERVAL_SEC)


if __name__ == "__main__":
    main()
