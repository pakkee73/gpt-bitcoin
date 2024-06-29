import pyupbit
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR, DAILY_CANDLE_COUNT, HOURLY_CANDLE_COUNT, SERPAPI_API_KEY
from utils.logger import get_logger

logger = get_logger()

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_with_retry(fetch_func, *args, **kwargs):
    return fetch_func(*args, **kwargs)

def validate_ohlcv_data(data):
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    return all(col in data.columns for col in required_columns)

def fetch_ohlcv_data():
    try:
        df_daily = fetch_with_retry(pyupbit.get_ohlcv, TRADING_PAIR, "day", count=DAILY_CANDLE_COUNT)
        df_hourly = fetch_with_retry(pyupbit.get_ohlcv, TRADING_PAIR, interval="minute60", count=HOURLY_CANDLE_COUNT)
        df_minute = fetch_with_retry(pyupbit.get_ohlcv, TRADING_PAIR, interval="minute1", count=60)  # 1분 데이터 추가
        
        if not validate_ohlcv_data(df_daily) or not validate_ohlcv_data(df_hourly) or not validate_ohlcv_data(df_minute):
            logger.error("Invalid OHLCV data structure")
            return None
        
        logger.debug(f"Daily OHLCV data:\n{df_daily.head()}")
        logger.debug(f"Hourly OHLCV data:\n{df_hourly.head()}")
        logger.debug(f"Minute OHLCV data:\n{df_minute.head()}")
        return {"daily": df_daily, "hourly": df_hourly, "1m": df_minute}
    except Exception as e:
        logger.error(f"Error fetching OHLCV data: {e}")
        return None

def fetch_orderbook():
    try:
        orderbook = fetch_with_retry(pyupbit.get_orderbook, ticker=TRADING_PAIR)
        logger.debug(f"Orderbook data:\n{orderbook}")
        return orderbook
    except Exception as e:
        logger.error(f"Error fetching orderbook: {e}")
        return None

def fetch_balance():
    try:
        balances = fetch_with_retry(upbit.get_balances)
        logger.debug(f"Fetched balances: {balances}")
        return balances
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return None

def fetch_fear_and_greed_index():
    try:
        url = "https://api.alternative.me/fng/"
        response = fetch_with_retry(requests.get, url, params={"limit": 30, "format": "json"})
        data = response.json()['data']
        logger.debug(f"Fear and Greed Index data:\n{data}")
        return data
    except Exception as e:
        logger.error(f"Error fetching Fear and Greed Index: {e}")
        return None

def fetch_all_data():
    ohlcv_data = fetch_ohlcv_data()
    balance_data = fetch_balance()
    orderbook_data = fetch_orderbook()
    fear_greed_data = fetch_fear_and_greed_index()
    
    if ohlcv_data is None or balance_data is None or orderbook_data is None or fear_greed_data is None:
        logger.error("Failed to fetch all required data")
        return None
    
    return {
        "ohlcv": ohlcv_data,
        "balance": balance_data,
        "orderbook": orderbook_data,
        "fear_greed": fear_greed_data
    }

if __name__ == "__main__":
    # 테스트 목적으로 함수 실행
    result = fetch_all_data()
    if result:
        logger.info("All data fetched successfully")
        logger.debug(f"Fetched data: {result}")
    else:
        logger.error("Failed to fetch all data")