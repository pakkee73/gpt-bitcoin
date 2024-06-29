from abc import ABC, abstractmethod

class TradingStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data):
        pass

class MovingAverageCrossover:
    def generate_signal(self, data):
        if 'ohlcv' not in data or '1m' not in data['ohlcv']:
            return 'hold'  # 데이터가 없으면 hold 신호 반환
        
        df = data['ohlcv']['1m']
        if 'SMA_5' not in df.columns or 'SMA_20' not in df.columns:
            return 'hold'  # SMA가 계산되지 않았으면 hold 신호 반환
        
        if df['SMA_5'].iloc[-1] > df['SMA_20'].iloc[-1] and df['SMA_5'].iloc[-2] <= df['SMA_20'].iloc[-2]:
            return 'buy'
        elif df['SMA_5'].iloc[-1] < df['SMA_20'].iloc[-1] and df['SMA_5'].iloc[-2] >= df['SMA_20'].iloc[-2]:
            return 'sell'
        return 'hold'

class RSIStrategy:
    def generate_signal(self, data):
        if 'ohlcv' not in data or '1m' not in data['ohlcv']:
            return 'hold'
        
        df = data['ohlcv']['1m']
        if 'RSI' not in df.columns:
            return 'hold'
        
        if df['RSI'].iloc[-1] < 30:
            return 'buy'
        elif df['RSI'].iloc[-1] > 70:
            return 'sell'
        return 'hold'

