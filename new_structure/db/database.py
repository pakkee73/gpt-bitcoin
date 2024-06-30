import sqlite3
from config import DB_PATH
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                result TEXT
            )
        ''')
        conn.commit()
        logger.info("Database initialized")

def save_decision(action, percentage, reason, btc_balance, krw_balance, btc_avg_buy_price):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO decisions (action, percentage, reason, btc_balance, krw_balance, btc_avg_buy_price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (action, percentage, reason, btc_balance, krw_balance, btc_avg_buy_price))
            conn.commit()
        logger.info(f"Decision saved: {action}, {percentage}, {reason}, {btc_balance}, {krw_balance}, {btc_avg_buy_price}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in save_decision: {e}")
        raise
        
def get_last_decisions(limit=10):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?', (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise

def get_recent_decisions(n):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, action, percentage, krw_balance, reason FROM decisions ORDER BY timestamp DESC LIMIT ?', (n,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise

def save_analysis_result(result):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO analysis_results (result) VALUES (?)', (str(result),))
            conn.commit()
        logger.info(f"Analysis result saved: {result}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise

def get_last_analysis_result():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM analysis_results ORDER BY timestamp DESC LIMIT 1')
            result = cursor.fetchone()
            if result:
                return {'timestamp': datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S'), 'result': eval(result[2])}
            return None
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
