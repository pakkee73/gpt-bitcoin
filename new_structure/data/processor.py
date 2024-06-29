import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger()

def add_indicators(df):
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
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
    df['RSI'] = df['RSI_14']  # RSI_14를 RSI로 변경
    return df

def process_ohlcv_data(ohlcv_data):
    processed = {}
    for timeframe, data in ohlcv_data.items():
        if isinstance(data, pd.DataFrame):
            if 'close' not in data.columns:
                if 'Close' in data.columns:
                    data = data.rename(columns={'Close': 'close'})
                else:
                    logger.error(f"Columns in {timeframe} data: {data.columns}")
                    raise ValueError(f"'close' column not found in {timeframe} data")
            
            data = add_indicators(data)
        else:
            logger.error(f"Unexpected data type for {timeframe}: {type(data)}")
            raise ValueError(f"Unexpected data type for {timeframe}")
        
        processed[timeframe] = data
    return processed

def process_data(raw_data):
    logger.debug(f"Raw OHLCV data keys: {raw_data['ohlcv'].keys()}")
    processed_data = {}
    processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])
    logger.debug(f"Processed OHLCV data keys: {processed_data['ohlcv'].keys()}")
    
    if '1m' in processed_data['ohlcv']:
        current_price = processed_data['ohlcv']['1m'].iloc[-1]['close']
    elif 'hourly' in processed_data['ohlcv']:
        current_price = processed_data['ohlcv']['hourly'].iloc[-1]['close']
    elif 'daily' in processed_data['ohlcv']:
        current_price = processed_data['ohlcv']['daily'].iloc[-1]['close']
    else:
        logger.error("No valid OHLCV data available for current price")
        raise ValueError("No valid OHLCV data available for current price")
    
    processed_data['current_price'] = current_price
    return processed_data