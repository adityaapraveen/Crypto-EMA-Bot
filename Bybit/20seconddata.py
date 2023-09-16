import ccxt.async_support as ccxt
import numpy as np
import pandas as pd
import time
import asyncio
    
# Set up your Phemex API credentials and initialize the exchange
api_key = 'lpJV7Miceg14bpjQHK'
api_secret = 'LVk84ojNpWw5609E4kC8hClLagyjdUa8ewCM'
exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})

# Define the trading parameters
symbol = 'BTC/USDT'
ema_5_period = 5
ema_40_period = 40
ema_50_period = 50

# Define the initial balance
initial_balance = 1000.0
balance = initial_balance
in_position = False
buy_price = 0


def calculate_ema(prices, period):
    ema = prices.ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]


def place_buy_order(price):
    global in_position, buy_price, balance
    amount = balance / price
    order = exchange.create_limit_buy_order(symbol, amount, price)
    print(f"Buy order placed at price: {price}")
    print(f"Order details: {order}")
    in_position = True
    buy_price = price


def place_sell_order(price):
    global in_position, balance
    amount = balance / price
    order = exchange.create_limit_sell_order(symbol, amount, price)
    profit = (price - buy_price) * balance
    balance += profit
    print(f"Sell order placed at price: {price}")
    print(f"Profit made: {profit}")
    print(f"New balance: {balance}")
    in_position = False


async def bot():
    last_order_time = 0
    while True:
        try:
            # Fetch the recent candlestick data
            candles = await exchange.fetch_ohlcv(symbol, timeframe='1m', limit=ema_50_period + 1)
            close_prices_50 = np.array([candle[4] for candle in candles])
            close_prices_50 = close_prices_50.astype(float)

            # Calculate the EMA values
            ema_5 = calculate_ema(pd.Series(close_prices_50), ema_5_period)
            ema_40 = calculate_ema(pd.Series(close_prices_50), ema_40_period)
            ema_50 = calculate_ema(pd.Series(close_prices_50), ema_50_period)

            print(f"EMA 5: {ema_5:.8f}, EMA 40: {ema_40:.8f}, EMA 50: {ema_50:.8f}")

            current_time = time.time()
            time_since_last_order = current_time - last_order_time

            if ema_5 is not None and ema_40 is not None and ema_50 is not None:
                if ema_5 > ema_40 and ema_5 > ema_50:
                    # Buy condition
                    if not in_position and time_since_last_order > 60:
                        place_buy_order(close_prices_50[-1])
                        last_order_time = current_time

                # Sell condition
                if in_position and (ema_5 <= ema_40 or ema_5 <= ema_50) and time_since_last_order > 60:
                    place_sell_order(close_prices_50[-1])
                    last_order_time = current_time

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        await asyncio.sleep(1)


asyncio.ensure_future(bot())
asyncio.get_event_loop().run_forever()