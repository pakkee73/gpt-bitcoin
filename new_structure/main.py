import schedule
import time
from data.fetcher import fetch_all_data
from data.processor import process_data
from analysis.claude_analyzer import analyze_data
from analysis.chart_analyzer import get_upbit_chart_image
from trading.strategy import decide_action, apply_stop_loss
from trading.executor import execute_trade
from utils.logger import setup_logger
from utils.alert_system import send_alert
from utils.performance_monitor import log_performance
from db.database import save_decision, initialize_db

logger = setup_logger()

def get_portfolio(raw_data):
    try:
        if 'error' in raw_data.get('balance', {}):
            logger.error(f"Error fetching balance: {raw_data['balance']['error']}")
            send_alert(f"Error fetching balance: {raw_data['balance']['error']}")
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
        send_alert(f"Error creating portfolio: {e}")
        return None

def trading_job():
    try:
        logger.info("Starting trading job")
        raw_data = fetch_all_data()
        logger.debug(f"Fetched raw data: {raw_data}")
        processed_data = process_data(raw_data)
        
        portfolio = get_portfolio(raw_data)
        if not portfolio:
            logger.error("Failed to get portfolio data. Skipping this trading cycle.")
            send_alert("Failed to get portfolio data. Skipping this trading cycle.")
            return
        
        current_price = processed_data.get('current_price')
        if not current_price:
            logger.error("Failed to get current price. Skipping this trading cycle.")
            send_alert("Failed to get current price. Skipping this trading cycle.")
            return
        
        logger.info(f"Current portfolio: {portfolio}")
        logger.info(f"Current BTC price: {current_price}")
        
        try:
            chart_image = get_upbit_chart_image()
            logger.info("Successfully captured chart image")
        except Exception as e:
            logger.error(f"Failed to capture chart image: {e}")
            send_alert(f"Failed to capture chart image: {e}")
            chart_image = None
        
        analysis_result = analyze_data(processed_data, chart_image)
        if not analysis_result:
            logger.error("Analysis failed. Skipping this trading cycle.")
            send_alert("Analysis failed. Skipping this trading cycle.")
            return
        logger.info(f"Analysis result: {analysis_result}")

        stop_loss_decision = apply_stop_loss(current_price, portfolio)
        if stop_loss_decision:
            decision = stop_loss_decision
            logger.info(f"Stop loss triggered: {decision}")
        else:
            decision = decide_action(analysis_result, current_price, portfolio)
            logger.info(f"Trading decision: {decision}")
        
        if decision['action'] != 'hold':
            result = execute_trade(decision)
            if result['success']:
                logger.info(f"Trade executed: {decision}")
                send_alert(f"Trade executed: {decision}")
            else:
                logger.error(f"Trade failed: {result['error']}")
                send_alert(f"Trade failed: {result['error']}")
        else:
            logger.info("Holding position. No trade executed.")
        
        save_decision(
            decision['action'],
            decision.get('percentage', 0),
            decision['reason'],
            portfolio['btc_balance'],
            portfolio['krw_balance'],
            portfolio['btc_avg_buy_price']
        )
        logger.info(f"Trading job completed. Decision: {decision}")
    except Exception as e:
        logger.error(f"Error in trading job: {e}", exc_info=True)
        send_alert(f"Trading Error: {str(e)}")

if __name__ == "__main__":
    try:
        initialize_db()
        logger.info("Database initialized")
        
        schedule.every(1).minutes.do(trading_job)  # 테스트를 위해 1분 간격으로 설정
        logger.info("Trading job scheduled to run every 1 minute")
        
        schedule.every(30).minutes.do(log_performance)
        logger.info("Performance logging scheduled to run every 30 minutes")
        
        logger.info("Starting main loop")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 대기
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                send_alert(f"Main Loop Error: {str(e)}")
                time.sleep(300)  # 5분 대기 후 재시도
    except Exception as e:
        logger.critical(f"Critical error in main script: {e}", exc_info=True)
        send_alert(f"Critical Error: {str(e)}")
