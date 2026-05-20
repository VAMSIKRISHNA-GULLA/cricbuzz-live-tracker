from sqlalchemy import Column, Integer, String
from database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    teamA = Column(String)
    teamB = Column(String)
    venue = Column(String)
    format = Column(String)