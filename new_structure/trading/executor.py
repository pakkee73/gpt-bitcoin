import pyupbit
from typing import Dict, Union
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR
from utils.logger import get_logger

logger = get_logger()

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def execute_trade(decision: Dict[str, Union[str, float]]) -> Dict[str, Union[bool, str, Dict]]:
    logger.info(f"Executing trade: {decision}")
    if decision['action'] == 'buy':
        return execute_buy(decision['percentage'])
    elif decision['action'] == 'sell':
        return execute_sell(decision['percentage'])
    else:
        logger.warning(f"Unknown action: {decision['action']}")
        return {"success": True, "message": "No action taken"}

def execute_buy(percentage: float) -> Dict[str, Union[bool, str, Dict]]:
    try:
        krw_balance = upbit.get_balance("KRW")
        amount = krw_balance * (percentage / 100)
        if amount < 5000:  # 최소 주문 금액
            logger.warning(f"Buy amount too small: {amount} KRW")
            return {'success': False, 'error': 'Buy amount too small'}
        result = upbit.buy_market_order(TRADING_PAIR, amount)
        logger.info(f"Buy order executed: {result}")
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Failed to execute buy order: {e}")
        return {'success': False, 'error': str(e)}

def execute_sell(percentage: float) -> Dict[str, Union[bool, str, Dict]]:
    try:
        btc_balance = upbit.get_balance(TRADING_PAIR.split('-')[1])
        amount = btc_balance * (percentage / 100)
        if amount * upbit.get_current_price(TRADING_PAIR) < 5000:  # 최소 주문 금액
            logger.warning(f"Sell amount too small: {amount} BTC")
            return {'success': False, 'error': 'Sell amount too small'}
        result = upbit.sell_market_order(TRADING_PAIR, amount)
        logger.info(f"Sell order executed: {result}")
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Failed to execute sell order: {e}")
        return {'success': False, 'error': str(e)}

def get_portfolio() -> Union[Dict[str, float], None]:
    try:
        balances = upbit.get_balances()
        krw_balance = next((float(b['balance']) for b in balances if b['currency'] == 'KRW'), 0)
        btc_balance = next((float(b['balance']) for b in balances if b['currency'] == 'BTC'), 0)
        btc_avg_buy_price = next((float(b['avg_buy_price']) for b in balances if b['currency'] == 'BTC'), 0)
        
        portfolio = {
            'krw_balance': krw_balance,
            'btc_balance': btc_balance,
            'btc_avg_buy_price': btc_avg_buy_price
        }
        logger.info(f"Current portfolio: {portfolio}")
        return portfolio
    except Exception as e:
        logger.error(f"Failed to get portfolio: {e}")
        return None

def get_current_portfolio() -> Union[Dict[str, float], None]:
    return get_portfolio()

__all__ = ['execute_trade', 'get_portfolio', 'get_current_portfolio']