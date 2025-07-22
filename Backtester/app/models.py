from sqlalchemy import Column,Integer,Float,String,DateTime
from app.database import Base
from datetime import datetime,timezone

class Trades(Base):
    __tablename__="trades"

    id=Column(Integer,primary_key=True,nullable=False)
    ticker=Column(String,nullable=False)
    price=Column(Float,nullable=False)
    quantity=Column(Integer,nullable=False)
    side=Column(String,nullable=False)
    timestamp=Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))