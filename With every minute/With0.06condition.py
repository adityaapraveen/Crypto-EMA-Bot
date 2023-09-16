import numpy as np
import pandas as pd
import time
import ta
import ccxt

# Set up your Phemex API credentials and initialize the exchange
api_key = '386e3334-a2d4-4afe-aa9e-6ebb9ca03496'
api_secret = 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'
exchange = ccxt.phemex({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})

def calculate_ema(close_prices, period):
    return ta.trend.ema_indicator(close_prices, period)

def bot(symbol, ema_5_period, ema_40_period, ema_50_period, initial_balance):
    balance = initial_balance
    in_position = False
    buy_price = 0
    
    def place_buy_order(price, balance):
        nonlocal in_position, buy_price
        amount = balance / price
        order = exchange.create_limit_buy_order(symbol, amount, price)
        print(f"Buy order placed at price: {price}")
        print(f"Current price: {exchange.fetch_ticker(symbol)['close']}")
        print(f"Order details: {order}")
        in_position = True
        buy_price = price

    def place_sell_order(price, balance):
        nonlocal in_position
        amount = balance / price
        order = exchange.create_limit_sell_order(symbol, amount, price)
        profit = (price - buy_price) * balance
        balance += profit
        print(f"Sell order placed at price: {price}")
        print(f"Profit made: {profit}")
        print(f"New balance: {balance}")
        in_position = False

    def sell_percentage(price, buy_price, percentage):
        return price >= buy_price * percentage
    
    while True:
        try:
            # Fetch the historical closing prices
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=ema_50_period + 1)
            close_prices = np.array([candle[4] for candle in candles])
            close_prices = close_prices.astype(float)  # Convert close prices to float

            if len(close_prices) >= ema_50_period:
                # Convert close prices to a pandas Series object
                close_series = pd.Series(close_prices)

                # Calculate the EMA values
                ema_5 = calculate_ema(close_series, ema_5_period)
                ema_40 = calculate_ema(close_series, ema_40_period)
                ema_50 = calculate_ema(close_series, ema_50_period)

                print(f"EMA 5: {ema_5.iloc[-1]:.8f}, EMA 40: {ema_40.iloc[-1]:.8f}, EMA 50: {ema_50.iloc[-1]:.8f}")

                if ema_5 is not None and ema_40 is not None and ema_50 is not None:
                    if ema_5.iloc[-1] > ema_40.iloc[-1] and ema_5.iloc[-1] > ema_50.iloc[-1]:
                        # Buy condition
                        if not in_position:
                            place_buy_order(close_prices[-1], balance)
                            time.sleep(60)  # Wait for sell order to be executed before placing another buy order

                    # Sell condition
                    if in_position and (ema_5.iloc[-1] <= ema_40.iloc[-1] or ema_5.iloc[-1] <= ema_50.iloc[-1] or sell_percentage(close_prices[-1], buy_price, 0.0006)):
                        place_sell_order(close_prices[-1], balance)
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        time.sleep(60)  # Change the sleep time as per your requirement

# Define the trading parameters
symbol = 'BTC/USDT'
ema_5_period = 5
ema_40_period = 40
ema_50_period = 50
initial_balance = 1000.0

bot(symbol, ema_5_period, ema_40_period, ema_50_period, initial_balance)