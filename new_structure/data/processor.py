import pandas as pd
import numpy as np

def add_indicators(df):
    # SMA
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    
    # EMA
    df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    
    return df

def process_ohlcv_data(ohlcv_data):
    for timeframe in ohlcv_data:
        ohlcv_data[timeframe] = add_indicators(ohlcv_data[timeframe])
    return ohlcv_data

def process_data(raw_data):
    processed_data = raw_data.copy()
    processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])
    return processed_data