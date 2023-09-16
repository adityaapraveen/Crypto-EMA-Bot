import ccxt
import pandas as pd

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


def calculate_profit(entry_price, exit_price, quantity):
    return (exit_price - entry_price) * quantity


def get_ema():
    print("STARTING INDICATORS...")

    timeframe = '1d'
    num_bars = 100

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
    total_profit = 0

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
    df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) &
             (df_d['EMA-50'] > df_d['EMA-5']), 'sig'] = 'SELL'
    df_d.loc[(df_d['EMA-40'] < df_d['EMA-5']) &
             (df_d['EMA-50'] < df_d['EMA-5']), 'sig'] = 'BUY'

    # if EMA-5 is in between EMA-40 and EMA-50

    df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) &
             (df_d['EMA-50'] < df_d['EMA-5']), 'sig'] = 'SELL'
    df_d.loc[(df_d['EMA-40'] < df_d['EMA-5']) &
             (df_d['EMA-50'] > df_d['EMA-5']), 'sig'] = 'SELL'

    for i in range(len(df_d)):
        if df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i] and df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]:
            print(f"Buy condition met at RS: {df_d['EMA-5'].iloc[i]}")
            if not active_positions:
                # Place limit buy order logic here
                buy_price = df_d['close'].iloc[i]
                place_buy_order(buy_price)
                active_positions.append(buy_price)

        if df_d['sig'].iloc[i] == 'SELL':
            if active_positions:
                # Place limit sell order logic here
                sell_price = df_d['close'].iloc[i]
                place_sell_order(sell_price)
                entry_price = active_positions.pop(0)
                profit = calculate_profit(entry_price, sell_price, pos_size)
                total_profit += profit
                print(f"Profit for this trade: {profit}")
                print(f"Total Profit: {total_profit}")
    df_d.dropna(inplace=True)

    pd.set_option('display.max_rows', None)
    print(df_d)


def place_buy_order(price):
    print(f"Placing buy order at price: {price}")
    # Example: phemex.create_limit_buy_order(symbol, pos_size, price)


def place_sell_order(price):
    print(f"Placing sell order at price: {price}")
    # Example: phemex.create_limit_sell_order(symbol, pos_size, price)


get_ema()
