import ccxt
import time

# Set up your Phemex API credentials
api_key = '386e3334-a2d4-4afe-aa9e-6ebb9ca03496'
api_secret = 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'

# Initialize the Phemex exchange
exchange = ccxt.phemex({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

# Define the trading parameters
symbol = 'BTC/USDT'
ema_5_period = 5
ema_40_period = 40
ema_50_period = 50
buy_threshold = 0.01  # Adjust this value based on your strategy
sell_threshold = 0.01  # Adjust this value based on your strategy
initial_balance = 1000.0  # Set your initial balance here

balance = initial_balance
in_position = False
buy_price = 0


def calculate_ema(data, period):
    # Calculate Exponential Moving Average (EMA)
    if len(data) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(data[-period:]) / period
    for price in data[-period - 1::-1]:
        ema = (price - ema) * k + ema
    return ema


def place_buy_order(price):
    global in_position, buy_price
    # Implement your buy order placement logic here
    # You should use exchange.create_market_buy_order() or exchange.create_limit_buy_order() to place a buy order
    print(f"Buy order placed at price: {price}")
    in_position = True
    buy_price = price


def place_sell_order(price):
    global balance, in_position
    # Implement your sell order placement logic here
    # You should use exchange.create_market_sell_order() or exchange.create_limit_sell_order() to place a sell order
    profit = (price - buy_price) * balance
    balance += profit
    print(f"Sell order placed at price: {price}")
    print(f"Profit made: {profit}")
    print(f"New balance: {balance}")
    in_position = False


def main():
    while True:
        try:
            # Fetch the latest candlestick data
            candles = exchange.fetch_ohlcv(
                symbol, timeframe='3600', limit=ema_50_period + 1)   #timeframe = 1h
            close_prices = [candle[4] for candle in candles]

            # Fetch the latest EMA values
            ema_5 = calculate_ema(close_prices, ema_5_period)

            # Fetch separate historical data for EMA 40 and EMA 50
            candles_40 = exchange.fetch_ohlcv(
                symbol, timeframe='3600', limit=ema_40_period + 1)
            close_prices_40 = [candle[4] for candle in candles_40]
            ema_40 = calculate_ema(close_prices_40, ema_40_period)

            candles_50 = exchange.fetch_ohlcv(
                symbol, timeframe='3600', limit=ema_50_period + 1)
            close_prices_50 = [candle[4] for candle in candles_50]
            ema_50 = calculate_ema(close_prices_50, ema_50_period)

            print(f"EMA 5: {ema_5}, EMA 40: {ema_40}, EMA 50: {ema_50}")

            if ema_5 is not None and ema_40 is not None:
                if ema_5 > ema_40:
                    # Buy condition
                    if ema_5 / ema_40 >= 1 + buy_threshold and not in_position:
                        # Buy at the latest close price
                        place_buy_order(close_prices[-1])

            if ema_5 is not None:
                if ema_5 >= ema_40 or ema_5 >= ema_50:
                    # Sell condition
                    if ema_5 / ema_40 <= 1 - sell_threshold or ema_5 / ema_50 <= 1 - sell_threshold:
                        if in_position:
                            # Sell at the latest close price
                            place_sell_order(close_prices[-1])

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for some time before checking again (adjust as needed)
        time.sleep(60)


if __name__ == '__main__':
    main()
