from sqlalchemy import Column,Integer,Float,String,DateTime,ForeignKey
from app.database import Base
from datetime import datetime,timezone
from sqlalchemy.sql import func

# base comes from databse helps in mapping sqlalchemy or registering tables
class User(Base):
    __tablename__="user"

    user_id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    email_id=Column(String)
    password=Column(String)
    created_at=Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))


class Backtest(Base):
    __tablename__="backtestrun"

    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    user_id=Column(Integer,nullable=False)
    strat_name=Column(String,nullable=False)
    symbol=Column(String,nullable=False)
    start_date=Column(DateTime,nullable=False)
    end_date=Column(DateTime,nullable=False)
    run_time=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
