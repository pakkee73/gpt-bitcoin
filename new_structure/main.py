import argparse
import schedule
import time
from data.fetcher import fetch_all_data
from data.processor import process_data
from analysis.claude_analyzer import analyze_data
from analysis.chart_analyzer import get_market_data
from trading.strategy import decide_action, apply_stop_loss
from trading.strategies import MovingAverageCrossover, RSIStrategy
from trading.executor import execute_trade
from utils.logger import get_logger
from utils.alert_system import send_alert
from utils.performance_monitor import log_performance
from db.database import save_decision, initialize_db
from dashboard.streamlit_app import run_dashboard

logger = get_logger()



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
        
        market_data = get_market_data()
        
        # 여러 트레이딩 전략 평가
        strategies = [MovingAverageCrossover(), RSIStrategy()]
        strategy_signals = []
        for strategy in strategies:
            try:
                signal = strategy.generate_signal(processed_data)
                strategy_signals.append(signal)
                logger.info(f"Strategy {strategy.__class__.__name__} signal: {signal}")
            except Exception as e:
                logger.error(f"Error in strategy {strategy.__class__.__name__}: {e}")
                strategy_signals.append('hold')  # 오류 발생 시 'hold' 신호 사용
        
        # Claude AI 분석
        analysis_result = analyze_data(processed_data, market_data.get('chart_image'))
        if not analysis_result:
            logger.error("Analysis failed. Using default strategy.")
            analysis_result = {'decision': 'hold', 'reason': 'Analysis failed', 'confidence': 0, 'suggested_position_size': 0}

        # 최종 트레이딩 결정 (strategy_signals는 참고용으로만 사용)
        final_decision = decide_action(analysis_result, current_price, portfolio)
        logger.info(f"Final trading decision: {final_decision}")
        
        if final_decision['action'] != 'hold':
            result = execute_trade(final_decision)
            if result['success']:
                logger.info(f"Trade executed: {final_decision}")
                send_alert(f"Trade executed: {final_decision}")
            else:
                logger.error(f"Trade failed: {result['error']}")
                send_alert(f"Trade failed: {result['error']}")
        else:
            logger.info("Holding position. No trade executed.")
        
        save_decision(
            final_decision['action'],
            final_decision.get('percentage', 0),
            final_decision['reason'],
            portfolio['btc_balance'],
            portfolio['krw_balance'],
            portfolio['btc_avg_buy_price']
        )
        logger.info(f"Trading job completed. Decision: {final_decision}")
    except Exception as e:
        logger.error(f"Error in trading job: {e}", exc_info=True)
        send_alert(f"Trading Error: {str(e)}")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin Trading Bot")
    parser.add_argument("--dashboard", action="store_true", help="Run the Streamlit dashboard")
    args = parser.parse_args()

    if args.dashboard:
        run_dashboard()
    else:
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
