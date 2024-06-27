import pyupbit
import requests
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR, DAILY_CANDLE_COUNT, HOURLY_CANDLE_COUNT, SERPAPI_API_KEY
from utils.logger import setup_logger

logger = setup_logger()

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def fetch_ohlcv_data():
    df_daily = pyupbit.get_ohlcv(TRADING_PAIR, "day", count=DAILY_CANDLE_COUNT)
    df_hourly = pyupbit.get_ohlcv(TRADING_PAIR, interval="minute60", count=HOURLY_CANDLE_COUNT)
    return {"daily": df_daily, "hourly": df_hourly}

def fetch_orderbook():
    return pyupbit.get_orderbook(ticker=TRADING_PAIR)

def fetch_balance():
    balances = upbit.get_balances()
    logger.debug(f"Fetched balances: {balances}")  # 디버그 로그 추가
    return balances

def fetch_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url, params={"limit": 30, "format": "json"})
    return response.json()['data']

def fetch_all_data():
    return {
        "ohlcv": fetch_ohlcv_data(),
        "orderbook": fetch_orderbook(),
        "balance": fetch_balance(),
        "fear_and_greed": fetch_fear_and_greed_index()
    }