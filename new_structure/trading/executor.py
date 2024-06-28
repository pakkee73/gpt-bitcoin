import pyupbit
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, TRADING_PAIR

upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def execute_trade(decision):
    if decision['action'] == 'buy':
        return execute_buy(decision['amount'])
    elif decision['action'] == 'sell':
        return execute_sell(decision['amount'])
    else:
         return {"success": True}
    
    return {"success": True}

def execute_buy(amount):
    try:
        result = upbit.buy_market_order(TRADING_PAIR, amount)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def execute_sell(amount):
    try:
        result = upbit.sell_market_order(TRADING_PAIR, amount)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
