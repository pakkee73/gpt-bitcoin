import matplotlib.pyplot as plt

def plot_price_and_indicators(df):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)

    # Price and Moving Averages
    ax1.plot(df.index, df['close'], label='Close Price')
    ax1.plot(df.index, df['SMA_10'], label='SMA 10')
    ax1.plot(df.index, df['EMA_10'], label='EMA 10')
    ax1.set_title('Bitcoin Price and Moving Averages')
    ax1.legend()

    # RSI
    ax2.plot(df.index, df['RSI_14'], label='RSI 14')
    ax2.axhline(y=70, color='r', linestyle='--')
    ax2.axhline(y=30, color='g', linestyle='--')