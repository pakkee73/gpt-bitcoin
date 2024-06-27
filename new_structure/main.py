import json
from data.fetcher import fetch_all_data
from data.processor import process_data
from analysis.claude_analyzer import analyze_data
from trading.strategy import decide_action, apply_stop_loss
from trading.executor import execute_trade
from utils.logger import setup_logger
from db.database import save_decision, initialize_db
import schedule
import time

logger = setup_logger()

def get_portfolio(raw_data):
    try:
        if 'error' in raw_data.get('balance', {}):
            logger.error(f"Error fetching balance: {raw_data['balance']['error']}")
            return None
        
        balances = raw_data.get('balance', [])
        krw_balance = next((float(b['balance']) for b in balances if b['currency'] == 'KRW'), 0)
        btc_balance = next((float(b['balance']) for b in balances if b['currency'] == 'BTC'), 0)
        btc_avg_buy_price = next((float(b['avg_buy_price']) for b in balances if b['currency'] == 'BTC'), 0)
        
        return {
            'krw_balance': krw_balance,
            'btc_balance': btc_balance,
            'btc_avg_buy_price': btc_avg_buy_price
        }
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        return None

def trading_job():
    try:
        logger.info("Starting trading job")
        logger.info("Fetching data...")
        raw_data = fetch_all_data()
        logger.debug(f"Raw data: {raw_data}")
        
        if 'error' in raw_data.get('balance', {}):
            logger.error(f"Failed to fetch balance data: {raw_data['balance']['error']}")
            return

        logger.info("Processing data...")
        processed_data = process_data(raw_data)
        logger.debug(f"Processed data: {processed_data}")
        
        # 현재 가격 정의
        current_price = processed_data['orderbook']['orderbook_units'][0]['ask_price']
        logger.info(f"Current price: {current_price}")

        logger.info("Analyzing data...")
        analysis_result = analyze_data(processed_data)
        logger.info(f"Analysis result: {analysis_result}")
        
        portfolio = get_portfolio(raw_data)
        logger.debug(f"Portfolio: {portfolio}")
        
        if portfolio is None:
            logger.error("Failed to create portfolio. Skipping this trading cycle.")
            return

        stop_loss_decision = apply_stop_loss(current_price, portfolio)
        if stop_loss_decision:
            decision = stop_loss_decision
        else:
            decision = decide_action(analysis_result, current_price, portfolio)
        
        if decision['action'] != 'hold':
            result = execute_trade(decision)
            if result['success']:
                logger.info(f"Trade executed: {decision}")
            else:
                logger.error(f"Trade failed: {result['error']}")
        
        save_decision(decision, portfolio['btc_balance'], portfolio['krw_balance'], portfolio['btc_avg_buy_price'])
        logger.info(f"Trading job completed. Decision: {decision}")
    except Exception as e:
        logger.error(f"Error in trading job: {e}", exc_info=True)

def run_trading_bot():
    logger.info("Starting Bitcoin trading bot")
    initialize_db()
    schedule.every(60).minutes.do(trading_job)
    
    logger.info("Executing first trading job immediately")
    trading_job()
    
    try:
        while True:
            logger.info("Waiting for next scheduled job...")
            schedule.run_pending()
            time.sleep(60)
            logger.info("Still running... (This message appears every minute)")
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user")
    except Exception as e:
        logger.error(f"Error in trading job: {e}", exc_info=True)

if __name__ == "__main__":
    run_trading_bot()