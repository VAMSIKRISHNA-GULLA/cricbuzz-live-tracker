from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    role = Column(String)

    batting_style = Column(String)

    bowling_style = Column(String)

    team = Column(String)

    match_id = Column(Integer, ForeignKey("matches.id"))