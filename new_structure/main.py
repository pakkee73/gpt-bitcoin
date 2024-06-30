import argparse
import schedule
import time
from functools import wraps
from data.processor import process_data
from analysis.claude_analyzer import analyze_data
from analysis.chart_analyzer import get_market_data
from trading.strategy import decide_action
from trading.executor import execute_trade, get_portfolio
from utils.logger import get_logger
from utils.alert_system import send_alert
from utils.performance_monitor import log_performance
from db.database import save_decision, initialize_db

logger = get_logger()

def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            send_alert(f"Error in {func.__name__}: {str(e)}")
    return wrapper

@error_handler
def get_and_process_data():
    market_data = get_market_data()
    if not market_data:
        raise ValueError("Failed to get market data")
    
    processed_data = process_data(market_data)
    if not processed_data:
        raise ValueError("Failed to process market data")
    
    return market_data, processed_data

@error_handler
def perform_analysis(processed_data):
    try:
        analysis_result = analyze_data(processed_data)
        if not analysis_result:
            logger.warning("Analysis failed. Using default strategy.")
            return {'decision': 'hold', 'reason': 'Analysis failed', 'confidence': 0, 'suggested_position_size': 0}
        return analysis_result
    except Exception as e:
        logger.error(f"Error in perform_analysis: {e}", exc_info=True)
        return {'decision': 'hold', 'reason': f'Analysis error: {str(e)}', 'confidence': 0, 'suggested_position_size': 0}

@error_handler
def execute_decision(final_decision):
    if final_decision['action'] != 'hold':
        result = execute_trade(final_decision)
        if result['success']:
            logger.info(f"Trade executed: {final_decision}")
            send_alert(f"Trade executed: {final_decision}")
        else:
            logger.error(f"Trade failed: {result['error']}")
            send_alert(f"Trade failed: {result['error']}")
    else:
        logger.info(f"Holding position. Reason: {final_decision['reason']}")

@error_handler
def trading_job():
    logger.info("Starting trading job")
    
    market_data, processed_data = get_and_process_data()
    
    portfolio = get_portfolio()
    if not portfolio:
        raise ValueError("Failed to get portfolio data")
    
    current_price = processed_data.get('current_price')
    if not current_price:
        raise ValueError("Failed to get current price")
    
    logger.info(f"Current portfolio: {portfolio}")
    logger.info(f"Current BTC price: {current_price}")
    
    analysis_result = perform_analysis(processed_data)
    logger.info(f"Analysis result: {analysis_result}")

    final_decision = decide_action(analysis_result, current_price, portfolio)
    logger.info(f"Final trading decision: {final_decision}")
    
    execute_decision(final_decision)
    
    save_decision(
        final_decision['action'],
        final_decision.get('percentage', 0),
        final_decision['reason'],
        portfolio['btc_balance'],
        portfolio['krw_balance'],
        portfolio['btc_avg_buy_price']
    )
    logger.info(f"Trading job completed. Decision: {final_decision}")

def main():
    try:
        initialize_db()
        logger.info("Database initialized")
        
        schedule.every(1).minutes.do(trading_job)
        logger.info("Trading job scheduled to run every 1 minute")
        
        schedule.every(30).minutes.do(log_performance)
        logger.info("Performance logging scheduled to run every 30 minutes")
        
        logger.info("Starting main loop")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received. Exiting gracefully...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                send_alert(f"Main Loop Error: {str(e)}")
                time.sleep(300)
    except Exception as e:
        logger.critical(f"Critical error in main script: {e}", exc_info=True)
        send_alert(f"Critical Error: {str(e)}")
    finally:
        logger.info("Shutting down the trading bot")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin Trading Bot")
    parser.add_argument("--dashboard", action="store_true", help="Run the Streamlit dashboard")
    args = parser.parse_args()

    if args.dashboard:
        from dashboard.streamlit_app import run_dashboard
        run_dashboard()
    else:
        main()