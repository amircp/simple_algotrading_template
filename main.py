import ccxt
import numpy as np
import pandas as pd
import os
import schedule
import time
from strategy import strategy, plot_strategy
import telegram
from tools import get_current_date
import asyncio
import sys

# Configuración de Binance API
api_key = os.environ.get("BINANCE_KEY")
api_secret = os.environ.get("BINANCE_SECRET")

binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultMarket': 'spot',
    },
})

TIME_FRAME = "15m"
SYMBOL = "BTC/USDT"

bot_token = os.environ.get('BOT_PIVOT_TOKEN')
chat_id = os.environ.get('PIVOT_CHAT_ID')


async def send_message_with_image(message, image_path=None):
    bot = telegram.Bot(token=bot_token)

    if image_path:
        with open(image_path, 'rb') as image_file:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='markdown')
            await bot.send_photo(chat_id=chat_id, photo=image_file)
    else:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='markdown')


def get_historical_data(symbol, timeframe):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'Close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # Establece la columna 'timestamp' como índice y conviértela en un DatetimeIndex
    df.set_index('timestamp', inplace=True)
    return df
    # You can use this method to get data feed from yahoo (just install yfinance and pandas data reader)
    # data = pdr.get_data_yahoo("QQQ", start='', end='')


position = False


def main():
    # Configuración de intervalo
    timeframe = '15m'


    def analyze_asset():

        df = get_historical_data(symbol, timeframe)
        trade, signal, data = strategy(df)
        if isinstance(data, pd.DataFrame):
            plot_strategy(data)

        global position

        if trade and signal:
            if signal == 'buy' and not position:
                position = True
                image_path = './graph.png'
                print(f"\033[96m{get_current_date()} - \033[92m[ BUY signal triggered ]")
                message = f" \[ ~ 📈*** Strategy Name *** 📈 ~ ]\r\n\r\n ✅ #{symbol} \r\n\r\n\r\nSignal: ***BUY*** \r\nCurrent Price: ***${data['Close'][-1]}***\r\nTF: ***{TIME_FRAME}***  \r\n"
                asyncio.run(send_message_with_image(message, image_path))
                os.remove(image_path)


            elif signal == "sell" and position:
                position = False
                image_path = './graph.png'
                message = f" \[ ~ 📈*** Strategy Name *** 📈 ~ ]\r\n\r\n ✅ #{symbol} \r\n\r\n\r\nSignal: ***SELL*** \r\nCurrent Price: ***${data['Close'][-1]}***\r\nTF: ***{TIME_FRAME}***  \r\n"
                asyncio.run(send_message_with_image(message, image_path))

                os.remove(image_path)

    analyze_asset()
    schedule.every(1).minutes.do(analyze_asset)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Ticker para tradear
    symbol = SYMBOL
    message = f" [ ~ 📈*** Strategy Name *** 📈 ~ ]\r\n\r\n ✅ #{symbol} \r\n\r\n\r\nStatus: ***Online*** \r\nTimeFrame: ***{TIME_FRAME}*** \r\n \r\n"

    print(message)

    asyncio.run(send_message_with_image(message))
    main()
