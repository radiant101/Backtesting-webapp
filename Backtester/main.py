from fastapi import FastAPI,Depends
from app.routes.yfinance_routes import router
from app.routes.other_routes import user_routes
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal
from app.models import Backtest
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.include_router(user_routes)
app.include_router(router)