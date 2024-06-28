import pyupbit
import requests
import pandas as pd
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR, DAILY_CANDLE_COUNT, HOURLY_CANDLE_COUNT, SERPAPI_API_KEY
from utils.logger import setup_logger

logger = setup_logger()

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def fetch_ohlcv_data():
    df_daily = pyupbit.get_ohlcv(TRADING_PAIR, "day", count=DAILY_CANDLE_COUNT)
    df_hourly = pyupbit.get_ohlcv(TRADING_PAIR, interval="minute60", count=HOURLY_CANDLE_COUNT)
    logger.debug(f"Daily OHLCV data:\n{df_daily.head()}")
    logger.debug(f"Hourly OHLCV data:\n{df_hourly.head()}")
    return {"daily": df_daily, "hourly": df_hourly}

def fetch_orderbook():
    orderbook = pyupbit.get_orderbook(ticker=TRADING_PAIR)
    logger.debug(f"Orderbook data:\n{orderbook}")
    return orderbook

def fetch_balance():
    balances = upbit.get_balances()
    logger.debug(f"Fetched balances: {balances}")
    return balances

def fetch_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url, params={"limit": 30, "format": "json"})
    logger.debug(f"Fear and Greed Index data:\n{response.json()}")
    return response.json()['data']

def fetch_all_data():
    return {
        "ohlcv": {
            "1m": pd.DataFrame({
                "timestamp": [1, 2, 3],
                "open": [100, 101, 102],
                "high": [105, 106, 107],
                "low": [95, 96, 97],
                "close": [102, 103, 104],  # 'close' 컬럼이 포함되어야 합니다.
                "volume": [10, 11, 12]
            }),
            # 다른 시간 프레임의 데이터도 추가할 수 있습니다
        },
        "balance": [
            {"currency": "KRW", "balance": "1000000", "avg_buy_price": "0"},
            {"currency": "BTC", "balance": "0.5", "avg_buy_price": "5000000"}
        ]
    }