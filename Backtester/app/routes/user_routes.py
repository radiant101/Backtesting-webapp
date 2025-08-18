from fastapi import APIRouter, HTTPException,status
from fastapi.responses import RedirectResponse
import yfinance as yf
import numpy as np
from app.schemas import Strategy_Input,Rsi_Input,user_create,user_out
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
from app import utils,models


router = APIRouter()
 

@router.post("/user",status_code=status.HTTP_201_CREATED,)
def create_user(user:user_create,db: Session= Depends(get_db)):
        #hash the user password 
        hashed_password=utils.hash_password(user.password)
        user.password=hashed_password
        user_data = user.model_dump()
        brun=User(**user_data)
        db.add(brun)
        db.commit()
        db.refresh(brun)
        return {'message' : 'created'}

@router.get("/user/{id}",response_model=user_out)
def get_user(id:int,db: Session= Depends(get_db)):
        user=db.query(models.User).filter(models.User.user_id==id).first()
        if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id :{id} does not exist")
        return  user