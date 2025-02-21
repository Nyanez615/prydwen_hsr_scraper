# scraper/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    rarity = Column(String, nullable=False)
    element = Column(String, nullable=False)
    path = Column(String, nullable=False)
    role = Column(String, nullable=False)
    moc_rating = Column(String)  # Store MoC rating as a string (or int if you prefer numeric)
    pf_rating = Column(String)
    as_rating = Column(String)
