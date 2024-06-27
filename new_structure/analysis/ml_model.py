from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

class BitcoinPricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_data(self, df):
        X = df[['open', 'high', 'low', 'close', 'volume', 'SMA_10', 'EMA_10', 'RSI_14', 'MACD']]
        y = df['close'].shift(-1)  # Predict next day's closing price
        X = X[:-1]  # Remove last row
        y = y[:-1]  # Remove last row
        return X, y

    def train(self, df):
        X, y = self.prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model MSE: {mse}")

    def predict(self, current_data):
        return self.model.predict(current_data.reshape(1, -1))[0]