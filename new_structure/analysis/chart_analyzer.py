import base64
import requests
import pandas as pd
import pyupbit
import plotly.graph_objects as go
from io import BytesIO
from utils.logger import get_logger

logger = get_logger()

def get_upbit_chart_data(interval='minutes', count=60):
    try:
        df = pyupbit.get_ohlcv("KRW-BTC", interval=interval, count=count)
        if df is None or df.empty:
            raise ValueError("Retrieved OHLCV data is empty")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch data from Upbit: {e}")
        return None

def create_chart_image(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])
    
    fig.update_layout(title='Bitcoin Price Chart', xaxis_title='Date', yaxis_title='Price')
    
    img_bytes = fig.to_image(format="png")
    return base64.b64encode(img_bytes).decode()

def calculate_indicators(df):
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    return df

def get_market_data():
    logger.info("Fetching Upbit chart data")
    chart_data = get_upbit_chart_data(interval="minute60", count=24)
    
    if chart_data is not None:
        logger.info("Successfully fetched chart data")
        chart_data = calculate_indicators(chart_data)
        chart_image = create_chart_image(chart_data)
        current_price = pyupbit.get_current_price("KRW-BTC")
        
        return {
            'chart_image': chart_image,
            'ohlcv': {
                'hourly': chart_data.reset_index().to_dict(orient='records')
            },
            'current_price': current_price,
            'chart_data': chart_data.reset_index().to_dict(orient='records')
        }
    else:
        logger.warning("Failed to fetch chart data, using placeholder image")
        return get_placeholder_data()

def get_placeholder_data():
    placeholder_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xcc\xed\xc3\x00\x00\x00\x00IEND\xaeB`\x82'
    return {
        'chart_image': base64.b64encode(placeholder_image).decode(),
        'ohlcv': {'hourly': []},
        'current_price': None,
        'chart_data': []
    }

if __name__ == "__main__":
    result = get_market_data()
    if result['chart_data']:
        logger.info("Chart data and image created successfully")
    else:
        logger.info("Using placeholder data")
    logger.debug(f"Market data: {result}")

__all__ = ['get_market_data']