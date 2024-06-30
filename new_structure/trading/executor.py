import pyupbit
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR
from utils.logger import get_logger

logger = get_logger()

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def execute_trade(decision):
    if decision['action'] == 'buy':
        return execute_buy(decision['percentage'])
    elif decision['action'] == 'sell':
        return execute_sell(decision['percentage'])
    else:
         return {"success": True}

def execute_buy(percentage):
    try:
        amount = upbit.get_balance("KRW") * (percentage / 100)
        result = upbit.buy_market_order(TRADING_PAIR, amount)
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Failed to execute buy order: {e}")
        return {'success': False, 'error': str(e)}

def execute_sell(percentage):
    try:
        amount = upbit.get_balance(TRADING_PAIR.split('-')[1]) * (percentage / 100)
        result = upbit.sell_market_order(TRADING_PAIR, amount)
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Failed to execute sell order: {e}")
        return {'success': False, 'error': str(e)}

def get_portfolio():
    try:
        balances = upbit.get_balances()
        krw_balance = next((float(b['balance']) for b in balances if b['currency'] == 'KRW'), 0)
        btc_balance = next((float(b['balance']) for b in balances if b['currency'] == 'BTC'), 0)
        btc_avg_buy_price = next((float(b['avg_buy_price']) for b in balances if b['currency'] == 'BTC'), 0)
        
        return {
            'krw_balance': krw_balance,
            'btc_balance': btc_balance,
            'btc_avg_buy_price': btc_avg_buy_price
        }
    except Exception as e:
        logger.error(f"Failed to get portfolio: {e}")
        return None