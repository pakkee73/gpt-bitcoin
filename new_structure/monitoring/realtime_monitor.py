import os
import websocket
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from utils.logger import get_logger

logger = get_logger()

def on_message(ws, message):
    data = json.loads(message)
    if is_important_event(data):
        send_alert(data)

def is_important_event(data):
    # 중요 이벤트 판단 로직
    # 예: 가격이 5% 이상 변동했을 때
    return False  # 실제 로직으로 대체해야 함

def send_alert(data):
    message = f"Important event: {data}"
    try:
        telegram_bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

def main():
    # 환경 변수에서 봇 토큰을 가져옵니다
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    global telegram_bot, CHAT_ID
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    if not CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID not found in environment variables")
        raise ValueError("TELEGRAM_CHAT_ID is not set")

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    telegram_bot = updater.bot

    # 웹소켓 연결
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                on_message=on_message)

    # 봇 시작
    updater.start_polling()

    # 웹소켓 연결 시작
    ws.run_forever()

if __name__ == '__main__':
    main()