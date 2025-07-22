from fastapi import FastAPI,Depends
from app.routes.yfinance_routes import router

from app.database import SessionLocal

app=FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(router)