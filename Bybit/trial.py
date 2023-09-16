import ccxt.async_support as ccxt
import numpy as np
import pandas as pd
import time
import asyncio
import json
import websockets
import talib

# Set up your Phemex API credentials and initialize the exchange
# ...

# Set up your Phemex API credentials and initialize the exchange
api_key = 'lpJV7Miceg14bpjQHK'
api_secret = 'LVk84ojNpWw5609E4kC8hClLagyjdUa8ewCM'
exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})

symbol = 'BTC/USDT'
ema_5_period = 5
ema_40_period = 40
ema_50_period = 50

# Define the initial balance
initial_balance = 1000.0
balance = initial_balance
in_position = False
buy_price = 0


async def bot():
    last_order_time = 0
    async with websockets.connect('wss://stream.bybit.com/realtime') as websocket:
        # Subscribe to the trade stream to receive live candlestick data
        await websocket.send('{"op": "subscribe", "args": ["kline.' + symbol + '.1m"]}')
        while True:
            try:
                data = await websocket.recv()
                json_data = json.loads(data)

                # Extract the candlestick data from the received stream data
                if 'success' in json_data and json_data['success'] and 'data' in json_data:
                    candle_data = json_data['data']['kline']
                    if len(candle_data) > ema_50_period + 1:
                        close_prices_50 = np.array([float(candle['close']) for candle in candle_data])
                
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