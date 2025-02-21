# scraper/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON

Base = declarative_base()

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    element = Column(String, nullable=False)
    path = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    role = Column(String, nullable=False)
    # Storing ratings as a JSON string; 
    # alternative is to create separate columns for each rating
    ratings = Column(JSON, nullable=True)
