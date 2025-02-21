# scraper/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraper.models import Base

# Create an SQLite engine (local file 'star_rail.db')
engine = create_engine('sqlite:///hsr.db', echo=True)

# Create a configured session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
