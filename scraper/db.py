# scraper/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraper.models import Base

engine = create_engine("sqlite:///hsr.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
