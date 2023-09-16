import ccxt
import pandas as pd
import time

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'rateLimit': 100,
    'apiKey': '386e3334-a2d4-4afe-aa9e-6ebb9ca03496',
    'secret': 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'
})
symbol = 'uBTCUSD'
pos_size = 50
params = {'timeInForce': 'PostOnly', }
target = 25


def get_ema():
    print("STARTING INDICATORS...")

    timeframe = '1d'
    num_bars = 100

    while True:
        bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_bars)

        df_d = pd.DataFrame(
            bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        df_d['timestamp'] = pd.to_datetime(df_d['timestamp'], unit='ms')

        timeframe = timeframe.replace('d', '')
        w = 2 / int(timeframe) + 1

        ema5 = [df_d['close'].iloc[0]]
        ema40 = [df_d['close'].iloc[0]]
        ema50 = [df_d['close'].iloc[0]]

        period5 = 5
        period40 = 40
        period50 = 50

        active_positions = []
        entry_price = 0  # Initialize entry_price

        for i in range(1, len(df_d)):
            ema5.append((df_d['close'][i] * 2 / (period5 + 1)) +
                        (ema5[i - 1] * (1 - 2 / (period5 + 1))))
        df_d['EMA-5'] = ema5

        for i in range(1, len(df_d)):
            ema40.append((df_d['close'][i] * 2 / (period40 + 1)) +
                         (ema40[i - 1] * (1 - 2 / (period40 + 1))))
        df_d['EMA-40'] = ema40

        for i in range(1, len(df_d)):
            ema50.append((df_d['close'][i] * 2 / (period50 + 1)) +
                         (ema50[i - 1] * (1 - 2 / (period50 + 1))))
        df_d['EMA-50'] = ema50

        # stop-loss percentage (1%)
        stop_loss_percent = 0.01

        for i in range(len(df_d)):
            for position in active_positions:
                entry_price, stop_loss_price = position
                if df_d['low'].iloc[i] <= stop_loss_price:
                    print(
                        f"Stop loss triggered at RS: {df_d['EMA-5'].iloc[i]}")
                    # Calculate profit
                    sell_price = df_d['EMA-5'].iloc[i]
                    profit = (sell_price - entry_price) * pos_size
                    print(f"Profit: {profit}")
                    # Remove the closed position
                    active_positions.remove(position)

            df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) &
                     (df_d['EMA-50'] > df_d['EMA-5']), 'sig'] = 'SELL'
            df_d.loc[(df_d['EMA-40'] < df_d['EMA-5']) &
                     (df_d['EMA-50'] < df_d['EMA-5']), 'sig'] = 'BUY'

            if df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i] and df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]:
                if entry_price == 0:  # Only update entry_price if it's not set already
                    entry_price = df_d['EMA-5'].iloc[i]  # Set entry_price
                    print(f"Buy condition met at RS: {entry_price}")

            elif (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
                if entry_price != 0:  # Only execute sell when there's an active position
                    print(
                        f"Sell condition 1 met at RS: {df_d['EMA-5'].iloc[i]}")
                    # Calculate profit
                    sell_price = df_d['EMA-5'].iloc[i]
                    profit = (sell_price - entry_price) * pos_size
                    print(f"Profit: {profit}")
                    entry_price = 0  # Reset entry_price

        df_d.dropna(inplace=True)

        pd.set_option('display.max_rows', None)
        print(df_d)
        time.sleep(600)  # Delay for 10 minutes before fetching new data


def bot(df_d):

    open_pos = False
    global current_direction  # Use the global flag

    for i in range(len(df_d)):
        price = df_d['EMA-5'].iloc[i]

        if df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i] and df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]:
            if current_direction != 'buy':
                print(f"Buy condition met at RS: {df_d['EMA-5'].iloc[i]}")
                current_direction = 'buy'
                # Place your limit buy order logic here
                # phemex.create_limit_buy_order(symbol, pos_size, price, params)
                open_pos = True  # Set the open_pos flag to True

        elif (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
            if current_direction != 'sell':

                print(f"Sell condition 1 met at RS: {df_d['EMA-5'].iloc[i]}")
                current_direction = 'sell'  # Set current direction to sell
                # Place your limit sell order logic for condition 1 here
                # phemex.create_limit_sell_order(symbol, pos_size, price, params)
                open_pos = False  # Set the open_pos flag to False after selling

        elif (df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
            if current_direction != 'sell':

                print(f"Buy condition met at RS: {df_d['EMA-5'].iloc[i]}")
                current_direction = 'sell'
                # Place your limit buy order logic here
                # phemex.create_limit_buy_order(symbol, pos_size, price, params)
                open_pos = True  # Set the open_pos flag to True

        # Add the third sell condition here
        elif (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
            if current_direction != 'sell':

                print(f"Sell condition 1 met at RS: {df_d['EMA-5'].iloc[i]}")
                # Place your limit sell order logic for condition 1 here
                # phemex.create_limit_sell_order(symbol, pos_size, price, params)
                open_pos = False  # Set the open_pos flag to False after selling


# bot(df_d)

get_ema()  # Start fetching live data and applying the trading logic
