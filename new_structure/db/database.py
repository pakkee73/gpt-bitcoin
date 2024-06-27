import sqlite3
from config import DB_PATH

def initialize_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT,
                percentage REAL,
                reason TEXT,
                btc_balance REAL,
                krw_balance REAL,
                btc_avg_buy_price REAL
            )
        ''')
        conn.commit()

def save_decision(decision, btc_balance, krw_balance, btc_avg_buy_price):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO decisions (action, percentage, reason, btc_balance, krw_balance, btc_avg_buy_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (decision['action'], decision['percentage'], decision['reason'], btc_balance, krw_balance, btc_avg_buy_price))
        conn.commit()

def get_last_decisions(limit=10):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cursor.fetchall()

# 필요한 경우 더 많은 데이터베이스 관련 함수들을 추가하세요