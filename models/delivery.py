from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(Integer, ForeignKey("matches.id"))

    over = Column(Integer)

    ball = Column(Integer)

    batsman = Column(String)

    bowler = Column(String)

    runs = Column(Integer)

    extra_type = Column(String, nullable=True)

    wicket = Column(String, nullable=True)