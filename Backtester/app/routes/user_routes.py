from fastapi import APIRouter, HTTPException,status
from fastapi.responses import RedirectResponse
import yfinance as yf
import numpy as np
from app.schemas import Strategy_Input,Rsi_Input,user_create,user_out,user_update,user_update_put
import os
import pandas as pd
from app.models import Backtest,User
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session
import plotly.express as px  
#from backtest.metrics import calculate_sharpe, calculate_maxdrawdown #has to work on
import time
from app.logic import moving_average_implementation,rsi_implementation  # Ensure your package structure supports this
from fastapi.responses import JSONResponse
from app import utils,models


router = APIRouter(
      prefix="/user"
)
 
#create a user
@router.post("/",status_code=status.HTTP_201_CREATED,)
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

#Read operation
@router.get("/{id}",response_model=user_out)
def get_user(id:int,db: Session= Depends(get_db)):
        user=db.query(models.User).filter(models.User.user_id==id).first()
        if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id :{id} does not exist")
        return  user

#Update operation
@router.put("/{id}")
def update_user(id:int,request_model: user_update_put,db: Session=Depends(get_db)):
      user=db.query(models.User).filter(models.User.user_id==id).first()
      if user==None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id :{id} doesnt exist")
      user_params=request_model.model_dump()
      for key,value in user_params.items():
            setattr(user,key,value)

      db.commit()
      db.refresh(user)
      return {f"updated with {id} succesfully"}

@router.patch("/{id}")
def update_user_patch(id:int,request_model:user_update, db: Session=Depends(get_db)):
     user=db.query(models.User).filter(models.User.user_id==id).first()
     if user is None:
           raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail=f"user with {id} not found"
           )
     user_params=request_model.model_dump(exclude_unset=True)
     for key,value in user_params.items():
           setattr(user,key,value)

     db.commit()
     db.refresh(user)
     return {"patched succesfully"}
     
#Delete operation
@router.delete("/{id}")
def delete_user(id:int,db:Session=Depends(get_db)):
      user_data=db.query(models.User).filter(models.User.user_id==id).first()
      if user_data==None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id :{id} doesnt exist")
      db.delete(user_data)
      db.commit()
      return {f"deleted user with {id} succesfully"}