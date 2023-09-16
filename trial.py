import ccxt
import pandas as pd
import time

# Configure your Phemex API credentials here
api_key = '386e3334-a2d4-4afe-aa9e-6ebb9ca03496'
api_secret = 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'
symbol = 'BTC/USDT'

exchange = ccxt.phemex({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

# Define the timeframes and corresponding EMA periods
timeframes = {
    '1m': {'ema_periods': [5, 40, 50]},
}


def calculate_ema(data, period):
    k = 2 / (period + 1)
    ema = data.iloc[0]['close']  # Initialize EMA with the first close price
    for i in range(1, len(data)):
        close = data.iloc[i]['close']
        ema = (close - ema) * k + ema
    return ema


while True:
    try:
        for timeframe, params in timeframes.items():
            # Fetch OHLCV data for the specified timeframe
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe)
            df = pd.DataFrame(
                ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            for period in params['ema_periods']:
                ema_column = f'EMA-{period}'
                df[ema_column] = df['close'].rolling(window=period).mean()

                # Calculate EMA for the most recent data point
                latest_ema = calculate_ema(df.tail(1), period)
                print(f'Timeframe: {timeframe}, {ema_column}: {latest_ema}')

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Sleep for 60 seconds before fetching data again
    time.sleep(60)
