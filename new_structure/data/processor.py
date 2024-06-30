import pandas as pd
from utils.logger import get_logger

logger = get_logger()

def add_indicators(df):
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    # Add more indicators as needed
    return df

def process_ohlcv_data(ohlcv_data):
    processed = {}
    for timeframe, data in ohlcv_data.items():
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            logger.error(f"Unexpected data type for {timeframe}: {type(data)}")
            continue
        
        if 'close' not in df.columns:
            if 'trade_price' in df.columns:
                df = df.rename(columns={'trade_price': 'close'})
            elif 'Close' in df.columns:
                df = df.rename(columns={'Close': 'close'})
            else:
                logger.error(f"'close' column not found in {timeframe} data")
                continue
        
        df = add_indicators(df)
        processed[timeframe] = df.to_dict(orient='records')
    
    return processed

def process_data(raw_data):
    if raw_data is None:
        logger.error("Raw data is None")
        return None

    logger.debug(f"Raw data keys: {raw_data.keys()}")
    processed_data = {}
    
    if 'ohlcv' in raw_data:
        processed_data['ohlcv'] = process_ohlcv_data(raw_data['ohlcv'])
    else:
        logger.error("'ohlcv' key not found in raw data")
        return None
    
    processed_data['current_price'] = raw_data.get('current_price')
    if processed_data['current_price'] is None:
        logger.error("Current price is missing from raw data")
        if 'hourly' in processed_data['ohlcv']:
            processed_data['current_price'] = processed_data['ohlcv']['hourly'][-1]['close']
            logger.warning("Using last hourly close price as current price")
        else:
            logger.error("Unable to determine current price")
            return None
    
    logger.info("Data processing completed successfully")
    return processed_data