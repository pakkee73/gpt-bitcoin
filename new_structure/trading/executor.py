import pyupbit
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR

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
        return {'success': False, 'error': str(e)}

def execute_sell(percentage):
    try:
        amount = upbit.get_balance(TRADING_PAIR.split('-')[1]) * (percentage / 100)
        result = upbit.sell_market_order(TRADING_PAIR, amount)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
def get_current_portfolio():
    return {'btc_balance': 0.5, 'krw_balance': 1000000}
    