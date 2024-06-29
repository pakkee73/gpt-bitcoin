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
        if isinstance(data, pd.DataFrame):
            if 'close' not in data.columns:
                # 'close' 컬럼이 없을 경우 'Close'로 시도
                if 'Close' in data.columns:
                    data = data.rename(columns={'Close': 'close'})
                else:
                    # 로그를 추가하여 현재 데이터 구조를 확인
                    logger.error(f"Columns in {timeframe} data: {data.columns}")
                    raise ValueError(f"'close' column not found in {timeframe} data")
        else:
            # DataFrame이 아닌 경우 로그 추가
            logger.error(f"Unexpected data type for {timeframe}: {type(data)}")
            raise ValueError(f"Unexpected data type for {timeframe}")
        
        processed[timeframe] = data
    return processed

def process_data(raw_data):
    processed_data = {}
    processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])

    logger.debug(f"Raw OHLCV data keys: {raw_data['ohlcv'].keys()}")
    processed_data = {}
    processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])
    logger.debug(f"Processed OHLCV data keys: {processed_data['ohlcv'].keys()}")
    
    # '1m' 데이터가 없을 경우 다른 시간프레임 사용
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