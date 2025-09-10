from fastapi import APIRouter
from fastapi import HTTPException
import yfinance as yf
import pandas as pd
import numpy as np
from io import StringIO
import os
from scipy.stats import zscore
from app.schemas import Strategy_Input,Rsi_Input
import requests
from datetime import timedelta

app=APIRouter()

'''def get_ohlc_data_from_yfinance(symbol, start_date, end_date):
    try:
        print(f"Entering download: start_date={start_date}, end_date={end_date} for symbol={symbol}")
        ticker = yf.Ticker(str(symbol))
        dt = ticker.history(start=str(start_date), end=str(end_date), interval="1d")
        if dt.empty:
            #raise ValueError(f"No data found between {start_date} and {end_date}")
        return dt  # Return the data if download is successful
    except Exception as e:
        print(f"Exception occurred: {e}")
         Optionally, re-raise the exception or handle it as needed
        raise
'''
def get_ohlc_data_from_alpha(symbol, start_date, end_date):
    API_KEY = "LNX0NFGULE1D1EK5"
    symbol = symbol
    print("going to url")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&datatype=csv&outputsize=full"
    response = requests.get(url)
    if response.ok:
     csv_data = response.text
     df=pd.read_csv(StringIO(csv_data)) #loading data
     df.rename(columns={'timestamp': 'date'}, inplace=True)
     df['date'] = pd.to_datetime(df['date'])
     filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
     print("data extracted")
     print(f"date range {df.head()}")
     print(f"getting out of ohlc alpha")
     return filtered_df
    else:
     print("Error:", response.status_code, response.text)

def moving_average_implementation(input: Strategy_Input):
    symbol = input.symbol
    start_date = input.start_date
    end_date = input.end_date
    short_window = input.short_window
    long_window = input.long_window

    # fetching data from alpha vantage
    ohlc_data = get_ohlc_data_from_alpha(symbol, start_date, end_date)
    if ohlc_data is None or ohlc_data.empty:
        raise HTTPException(status_code=404, detail="failed to load data.")

    ohlc_data = ohlc_data[np.abs(zscore(ohlc_data["close"])) < 3]
    print("before moving-average function:")
    resample_interval = '1d'
    ohlc_data = moving_average(ohlc_data, short_window, long_window, resample_interval)
    print("after moving-average function:")
    # Saving data to CSV and returning  its path.
    csv_file_path = os.path.join(os.getcwd(), f"{symbol}_ohlc_data.csv")
    ohlc_data.to_csv(csv_file_path, index=False)
    return csv_file_path

def moving_average(df, short_window,long_window,resample_interval='1h'):
    df['date'] = pd.to_datetime(df['date'])
    
    # Set the 'date' column as the index for resampling
    df.set_index('date', inplace=True)
    
    # Resample data to the specified interval
    ohlc_resampled = df.resample(resample_interval).agg({
        'open':'first',
        'high':'max',
        'low':'min',
        'close':'last',
        'volume':'sum'
    }).dropna()
    
    #resampling
    ohlc_resampled.reset_index(inplace=True)
    
    # Calculate moving averages on the resampled data
    ohlc_resampled['short_ma'] = ohlc_resampled['close'].rolling(window=short_window).mean()
    ohlc_resampled['long_ma'] = ohlc_resampled['close'].rolling(window=long_window).mean()
    
    # Add buy/sell signal columns
    ohlc_resampled['signal'] = 0
    ohlc_resampled.loc[ohlc_resampled['short_ma'] > ohlc_resampled['long_ma'], 'signal'] = 1
    ohlc_resampled.loc[ohlc_resampled['short_ma'] < ohlc_resampled['long_ma'], 'signal'] = -1

    return ohlc_resampled


def rsi_implementation(input:Rsi_Input):
   symbol=input.symbol
   start_date=input.start_date
   end_date=input.end_date
   adjusted_start_date=start_date-timedelta(days=15)
   ohlc_data=get_ohlc_data_from_alpha(symbol,adjusted_start_date,end_date)
   # when i am stating start date i have to go beyond 14 days for my lookback period
   # to calculate average gain and loss
   if ohlc_data is None or ohlc_data.empty:
      raise HTTPException(status_code=400,detail="failed to load data")

   df=ohlc_data
   df["change"]=df["close"].diff()

   # here i am using apply from pandas which uses a lambda function
   df['gain']=df['change'].apply(lambda x: x if x>0 else 0)
   df['loss']=df['change'].apply(lambda x: -x if x<0 else 0)

   df['avg_gain']=df['gain'].rolling(14).mean()
   df['avg_loss']=df['loss'].rolling(14).mean()

   # rsi
   df['rs']=df['avg_gain']/df['avg_loss']
   df['rsi']=100-(100/(1+df['rs']))
   #signals
   df['buy']=df['rsi'].apply(lambda x: 1 if x<30 else 0)
   df['sell']=df['rsi'].apply(lambda x: -1 if x>70 else 0)
   print('after rsi')
   #ya nanataar iterate kar rsi coloumn var and generate buy and sell signal \
   
   csv_file_path = os.path.join(os.getcwd(), f"{symbol}_ohlc_data.csv")
   df.to_csv(csv_file_path, index=False)
   return csv_file_path