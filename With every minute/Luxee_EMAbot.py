import ccxt
import numpy as np
import time
from ta.trend import EMAIndicator
import pandas as pd

# Set up your Phemex API credentials and initialize the exchange
api_key = '386e3334-a2d4-4afe-aa9e-6ebb9ca03496'
api_secret = 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'
    
exchange = ccxt.phemex({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})

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

def calculate_ema(data, period):
    # Calculate Exponential Moving Average (EMA)
    if len(data) < period:
        return None

    df = pd.DataFrame(data, columns=["close"])
    ema = df["close"].ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]


def place_buy_order(price):
    global in_position, buy_price
    amount = balance / price
    order = exchange.create_limit_buy_order(symbol, amount, price)
    print(f"Buy order placed at price: {price}")
    print(f"Order details: {order}")
    in_position = True
    buy_price = price


def place_sell_order(price):
    global balance, in_position
    amount = balance / price
    order = exchange.create_limit_sell_order(symbol, amount, price)
    profit = (price - buy_price) * balance
    balance += profit
    print(f"Sell order placed at price: {price}")
    print(f"Profit made: {profit}")
    print(f"New balance: {balance}")
    in_position = False
    

def main():
    last_order_time = 0
    while True:
        try:
            # Fetch the historical closing prices
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=ema_50_period + 1)
            close_prices = np.array([candle[4] for candle in candles])

            if len(close_prices) >= ema_50_period:
                # Calculate the EMA values
                ema_5 = calculate_ema(close_prices, ema_5_period)
                ema_40 = calculate_ema(close_prices, ema_40_period)
                ema_50 = calculate_ema(close_prices, ema_50_period)

                print(f"EMA 5: {ema_5}, EMA 40: {ema_40}, EMA 50: {ema_50}")

                current_time = time.time()
                time_since_last_order = current_time - last_order_time

                if ema_5 is not None and ema_40 is not None and ema_50 is not None:
                    if ema_5 > ema_40 and ema_5 > ema_50:
                        # Buy condition
                        # Add a time threshold (60 seconds here) to prevent consecutive orders
                        if not in_position and time_since_last_order > 60:
                            place_buy_order(close_prices[-1])
                            last_order_time = current_time

                    # Sell condition
                    if in_position and (ema_5 <= ema_40 or ema_5 <= ema_50) and time_since_last_order > 60:
                        place_sell_order(close_prices[-1])
                        last_order_time = current_time

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for some time before checking again (adjust as needed)
        time.sleep(60)  # Change the sleep time as per your requirement


if __name__ == '__main__':
    main()