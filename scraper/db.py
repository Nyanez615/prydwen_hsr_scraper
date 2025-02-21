# scraper/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraper.models import Base

# Default: local hsr.db
# If you want a dynamic DB_URL, you can read from environment here.
engine = create_engine(os.environ.get('DB_URL', 'sqlite:///hsr.db'), echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)