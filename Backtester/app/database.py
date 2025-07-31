from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

Database_URL="postgresql://postgres:admin@localhost:5432/tradedb"



engine=create_engine(Database_URL)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)


Base = declarative_base()
import app.models

Base.metadata.create_all(bind=engine)

def get_db():
     db=SessionLocal()
     try:
          yield db
          print("connected to database")
     finally:
          db.close()