import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")  # 이 줄이 있는지 확인하세요

DB_PATH = 'trading_decisions.sqlite'
TRADING_PAIR = "KRW-BTC"
DAILY_CANDLE_COUNT = 30
HOURLY_CANDLE_COUNT = 24

LOG_FILE = "trading.log"

TRADING_INTERVAL = 60  # 60분마다 거래

# 새로 추가된 변수들
MAX_POSITION_SIZE = 0.1  # 전체 자산의 최대 10%까지 포지션 가능
STOP_LOSS_PERCENTAGE = 0.05  # 5% 손실 시 손절

# 이메일 설정
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")