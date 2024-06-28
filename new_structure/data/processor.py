import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger()

def add_indicators(df):
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    return df

def process_ohlcv_data(ohlcv_data):
    processed = {}
    for timeframe, data in ohlcv_data.items():
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        elif isinstance(data, pd.DataFrame):
            data = data.T
        
        if 'close' not in data.columns:
            raise ValueError(f"'close' column not found in {timeframe} data")
        
        processed[timeframe] = data
    return processed

def process_data(raw_data):
    processed_data = {}
    processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])
    processed_data['current_price'] = processed_data['ohlcv']['1m'].iloc[-1]['close']
    return processed_data