from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import yfinance as yf
import numpy as np
from app.schemas import Strategy_Input,Rsi_Input
import os
import pandas as pd
from app.models import Backtest
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session
import plotly.express as px  # Import Plotly Express for charting
#from backtest.metrics import calculate_sharpe, calculate_maxdrawdown #has to work on
import time
from app.logic import moving_average_implementation,rsi_implementation  # Ensure your package structure supports this
from fastapi.responses import JSONResponse
router = APIRouter()

def helperfunc(inputdict):
    db_fields={
        "user_id":0,
        "strat_name":inputdict['strat_name'],
        "symbol":inputdict['symbol'],
        "start_date":inputdict['start_date'],
        "end_date":inputdict['end_date'],
    }
    return db_fields
@router.post("/strategy/")
async def strategy_endpoint(input: Strategy_Input, db: Session= Depends(get_db)):
    try:
        input_data = input.model_dump()
        db_insert=helperfunc(input_data)
        brun=Backtest(**db_insert)
        db.add(brun)
        db.commit()
        db.refresh(brun)
        print("added to db")
        csv_path = moving_average_implementation(input)
        redirect_url = f"http://127.0.0.1:8000/result.html?symbol={input.symbol}&short_window={input.short_window}&long_window={input.long_window}"
        return JSONResponse(content={"redirect_url": redirect_url})
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")
    except Exception as e:
        print(f"Unexpected exception: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.post("/strategy/rsi")
async def rsi_endpoint(input : Rsi_Input):
    try:
        rsi_implementation(input)
        print("came out of rsi_implement")
        redirect_url = f"/result/rsi?symbol={input.symbol}"
        return RedirectResponse(url=redirect_url,status_code=303)
    except Exception as e:
        print(f"unexpected exception{e}")
        raise HTTPException(status_code=500,detail=f"an error occured during reaching endpoint {e}")


@router.get("/result/")
async def results_endpoint(symbol: str, short_window: int, long_window: int):
    # Construct the CSV file path using the symbol
    csv_file_path = os.path.join(os.getcwd(), f"{symbol}_ohlc_data.csv")
    if not os.path.exists(csv_file_path):
        raise HTTPException(status_code=404, detail="CSV file not found.")

    start_time = time.time()
    ohlc_data = pd.read_csv(csv_file_path)
    #sharpe_val = calculate_sharpe(csv_file_path)
    #max_drawdown = calculate_maxdrawdown(csv_file_path)

    # Parse the date column for plotting
    ohlc_data['date'] = pd.to_datetime(ohlc_data['date'])
    print(f"CSV loaded in {time.time() - start_time:.2f} seconds.")
    print(f"Dataframe shape: {ohlc_data.shape}")

    # Create a Plotly line chart
    fig = px.line(
        ohlc_data,
        x='date',
        y=['short_ma', 'long_ma', 'close'],  # Ensure these column names match your CSV
        title=f"Backtesting Results for {symbol} ({short_window}-{long_window})",
        labels={'value': 'Price', 'variable': 'Legend'},
        template='plotly_dark'
    )
    chart_json = fig.to_json()
    print("Plotly chart created successfully.")

    # Return results as JSON (alternatively, you could render an HTML template)
    return {
        "chart_json": chart_json,
        #"sharpe_val": sharpe_val,
        #"max_drawdown": max_drawdown
    }

@router.get("/result/rsi")
async def results_rsiendpoint(symbol:str):
    csv_file_path=os.path.join(os.getcwd(),f"{symbol}_ohlc_data.csv")
    if not os.path.exists(csv_file_path):
        raise HTTPException(status_code=400,detail=f"file not found") 
    ohlc_data = pd.read_csv(csv_file_path)
    ohlc_data['date'] = pd.to_datetime(ohlc_data['date'])

    if 'rsi' not in ohlc_data.columns:
     raise HTTPException(status_code=400, detail="RSI column not found in CSV")

    fig = px.line(
    ohlc_data,
    x='date',
    y='rsi',  # column that stores RSI values
    title=f"RSI Indicator for {symbol}",
    labels={'rsi': 'RSI Value'},
    template='plotly_dark'
    ) 
    chart_json = fig.to_json()
    print("rssi chart created successfully.")

    # Return results as JSON (alternatively, you could render an HTML template)
    return {
        "status": "success",
        "chart_json": chart_json,
        #"sharpe_val": sharpe_val,
        #"max_drawdown": max_drawdown
    }