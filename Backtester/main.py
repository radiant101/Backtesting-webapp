from fastapi import FastAPI,Depends
from app.routes.yfinance_routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal

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


app.include_router(router)