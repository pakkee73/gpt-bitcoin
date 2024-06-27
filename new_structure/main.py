import schedule
import time
from data.fetcher import fetch_all_data
from data.processor import process_data
from analysis.claude_analyzer import analyze_data
from trading.strategy import decide_action, apply_stop_loss
from trading.executor import execute_trade
from utils.logger import setup_logger
from db.database import save_decision, initialize_db
from config import TRADING_INTERVAL

logger = setup_logger()

def get_portfolio(raw_data):
    try:
        return {
            'krw_balance': float(raw_data['balance'][0]['balance']),
            'btc_balance': float(raw_data['balance'][1]['balance']),
            'btc_avg_buy_price': float(raw_data['balance'][1]['avg_buy_price'])
        }
    except (IndexError, KeyError) as e:
        logger.error(f"Error creating portfolio: {e}")
        return None

def execute_decision(decision, current_price):
    if decision['action'] != 'hold':
        result = execute_trade(decision)
        if result['success']:
            logger.info(f"Trade executed: {decision}")
        else:
            logger.error(f"Trade failed: {result['error']}")
    else:
        logger.info(f"Holding position. Current price: {current_price}")

def trading_job():
    try:
        logger.info("Starting trading job")
        logger.info("Fetching data...")
        raw_data = fetch_all_data()
        logger.info("Processing data...")
        processed_data = process_data(raw_data)
        logger.info("Analyzing data...")
        analysis_result = analyze_data(processed_data)
        
        if analysis_result is None:
            logger.error("Data analysis failed. Skipping this trading cycle.")
            return

        logger.info(f"Analysis result: {analysis_result}")

        stop_loss_decision = apply_stop_loss(current_price, portfolio)
        if stop_loss_decision:
            logger.info("Stop loss triggered")
            decision = stop_loss_decision
        else:
            logger.info("Making trading decision...")
            decision = decide_action(analysis_result, current_price, portfolio)
        
        logger.info(f"Decision made: {decision}")
        execute_decision(decision, current_price)
        
        logger.info("Saving decision to database...")
        save_decision(decision, portfolio['btc_balance'], portfolio['krw_balance'], portfolio['btc_avg_buy_price'])
        logger.info(f"Trading job completed. Decision: {decision}")
    except Exception as e:
        logger.error(f"Error in trading job: {e}", exc_info=True)

def run_trading_bot():
    logger.info("Starting Bitcoin trading bot")
    initialize_db()
    schedule.every(TRADING_INTERVAL).minutes.do(trading_job)
    
    logger.info(f"Trading job scheduled to run every {TRADING_INTERVAL} minutes")
    logger.info("Executing first trading job immediately")
    trading_job()  # 즉시 첫 번째 trading_job 실행
    
    try:
        while True:
            logger.info("Waiting for next scheduled job...")
            schedule.run_pending()
            time.sleep(60)  # 1분마다 로그 출력
            logger.info("Still running... (This message appears every minute)")
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    run_trading_bot()