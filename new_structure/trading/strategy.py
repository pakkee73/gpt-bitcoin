from config import MAX_POSITION_SIZE, STOP_LOSS_PERCENTAGE

def decide_action(analysis_result, current_price, portfolio):
    action = analysis_result['decision']['action']
    confidence = analysis_result['decision']['confidence']
    
    if action == 'buy':
        return execute_buy(confidence, current_price, portfolio)
    elif action == 'sell':
        return execute_sell(confidence, current_price, portfolio)
    else:
        return {'action': 'hold', 'amount': 0, 'reason': 'No clear signal'}

def execute_buy(confidence, current_price, portfolio):
    max_buy_amount = portfolio['krw_balance'] * MAX_POSITION_SIZE
    buy_amount = max_buy_amount * (confidence / 100)
    
    if buy_amount < 5000:  # 최소 주문 금액
        return {'action': 'hold', 'amount': 0, 'reason': 'Buy amount too small'}
    
    return {
        'action': 'buy',
        'amount': buy_amount,
        'reason': f'Buy signal with {confidence}% confidence'
    }

def execute_sell(confidence, current_price, portfolio):
    btc_balance = float(portfolio['btc_balance'])
    max_sell_amount = btc_balance * MAX_POSITION_SIZE
    sell_amount = max_sell_amount * (confidence / 100)
    
    if sell_amount * current_price < 5000:  # 최소 주문 금액
        return {'action': 'hold', 'amount': 0, 'reason': 'Sell amount too small'}
    
    return {
        'action': 'sell',
        'amount': sell_amount,
        'reason': f'Sell signal with {confidence}% confidence'
    }

def apply_stop_loss(current_price, portfolio):
    avg_buy_price = float(portfolio['btc_avg_buy_price'])
    if current_price < avg_buy_price * (1 - STOP_LOSS_PERCENTAGE):
        return {
            'action': 'sell',
            'amount': float(portfolio['btc_balance']),
            'reason': 'Stop loss triggered'
        }
    return None