import pandas as pd
import numpy as np
import mplfinance as mpf


def strategy(df):
    # Strategy Here

    if df.iloc[-1]['buy_signal'] > 0:
        return True, "buy", df

    if df.iloc[-1]['sell_signal'] > 0:
        return True, "sell", df

    return False, "hold", df


def plot_strategy(df):
    df['Buy_Price'] = np.where(df['buy_signal'], df['Close'], np.nan)
    df['Sell_Price'] = np.where(df['sell_signal'], df['Close'], np.nan)

    subplots = [mpf.make_addplot(df['Buy_Price'], markersize=100, type='scatter', marker='^', color='g'),
                mpf.make_addplot(df['Sell_Price'], markersize=100, type='scatter', marker='v', color='r')]

    fig, axes = mpf.plot(df, style='binance', savefig='graph.png', type='candle', returnfig=True, addplot=subplots,
                         ylabel='Price', title='Strategy Name', figsize=(20, 10),
                         show_nontrading=True, volume=False)
