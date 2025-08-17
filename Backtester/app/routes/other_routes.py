from fastapi import APIRouter, HTTPException,status
from fastapi.responses import RedirectResponse
import yfinance as yf
import numpy as np
from app.schemas import Strategy_Input,Rsi_Input,user_create
import os
import pandas as pd
from app.models import Backtest,User
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session
import plotly.express as px  # Import Plotly Express for charting
#from backtest.metrics import calculate_sharpe, calculate_maxdrawdown #has to work on
import time
from app.logic import moving_average_implementation,rsi_implementation  # Ensure your package structure supports this
from fastapi.responses import JSONResponse
user_routes = APIRouter()

@user_routes.post("/user",status_code=status.HTTP_201_CREATED,)
def create_user(user:user_create,db: Session= Depends(get_db)):
        user_data = user.model_dump()
        brun=User(**user_data)
        db.add(brun)
        db.commit()
        db.refresh(brun)
        return {'message' : 'created'}