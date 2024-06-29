from config import MAX_POSITION_SIZE, STOP_LOSS_PERCENTAGE

def decide_action(analysis_result, current_price, portfolio):
    action = analysis_result.get('decision', 'hold')
    confidence = analysis_result.get('confidence', 0)
    suggested_position_size = analysis_result.get('suggested_position_size', 0)

    if action == 'buy':
        return execute_buy(confidence, suggested_position_size, current_price, portfolio)
    elif action == 'sell':
        return execute_sell(confidence, suggested_position_size, current_price, portfolio)
    else:
        return {"action": "hold", "percentage": 0, "reason": "No action needed"}

def execute_buy(confidence, suggested_position_size, current_price, portfolio):
    max_buy_amount = min(portfolio['krw_balance'] * MAX_POSITION_SIZE, portfolio['krw_balance'] * (suggested_position_size / 100))
    buy_amount = max_buy_amount * (confidence / 100)
    
    if buy_amount < 5000:  # 최소 주문 금액
        return {'action': 'hold', 'percentage': 0, 'reason': 'Buy amount too small'}
    
    return {
        'action': 'buy',
        'percentage': (buy_amount / portfolio['krw_balance']) * 100,
        'reason': f'Buy signal with {confidence}% confidence'
    }

def execute_sell(confidence, suggested_position_size, current_price, portfolio):
    max_sell_amount = min(portfolio['btc_balance'] * MAX_POSITION_SIZE, portfolio['btc_balance'] * (suggested_position_size / 100))
    sell_amount = max_sell_amount * (confidence / 100)
    
    if sell_amount * current_price < 5000:  # 최소 주문 금액
        return {'action': 'hold', 'percentage': 0, 'reason': 'Sell amount too small'}
    
    return {
        'action': 'sell',
        'percentage': (sell_amount / portfolio['btc_balance']) * 100,
        'reason': f'Sell signal with {confidence}% confidence'
    }

def apply_stop_loss(current_price, portfolio):
    if current_price < portfolio['btc_avg_buy_price'] * (1 - STOP_LOSS_PERCENTAGE):
        return {
            'action': 'sell',
            'amount': portfolio['btc_balance'],
            'reason': 'Stop loss triggered'
        }
    return None

def optimize_strategy(strategy, historical_data):
    # 백테스팅 및 최적화 로직 구현
    pass