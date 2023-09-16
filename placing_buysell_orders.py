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
params = {'timeInForce': 'PostOnly'}
target = 25

active_positions = []
waiting_for_signal = None


def place_limit_order(side, price):
    try:
        if side == 'BUY':
            order = phemex.create_limit_buy_order(
                symbol, pos_size, price, params)
            print(f"Placed BUY order at price: {price}")
        elif side == 'SELL':
            order = phemex.create_limit_sell_order(
                symbol, pos_size, price, params)
            print(f"Placed SELL order at price: {price}")
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None


def handle_signal(signal, price):
    global waiting_for_signal
    if waiting_for_signal is None:
        if signal == 'BUY':
            order = place_limit_order('BUY', price)
            if order:
                active_positions.append(
                    (order['price'], order['price'] - (order['price'] * stop_loss_percent)))
                waiting_for_signal = 'SELL'
        elif signal == 'SELL':
            order = place_limit_order('SELL', price)
            if order:
                active_positions.append(
                    (order['price'], order['price'] + (order['price'] * stop_loss_percent)))
                waiting_for_signal = 'BUY'
    elif waiting_for_signal == signal:
        # Continue waiting for the same signal
        pass
    else:
        # Signal changed, close existing position
        close_position(signal, price)
        waiting_for_signal = signal


def close_position(signal, price):
    global active_positions
    for position in active_positions:
        entry_price, stop_loss_price = position
        if signal == 'BUY':
            if price >= entry_price:
                order = place_limit_order('SELL', price)
                if order:
                    active_positions.remove(position)
        elif signal == 'SELL':
            if price <= entry_price:
                order = place_limit_order('BUY', price)
                if order:
                    active_positions.remove(position)


def get_ema():
    # Rest of your code as it is
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

    buy_signal_triggered = False
    sell_signal_triggered = False

    # Placeholder for 'sig' assignments based on your conditions
    if df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) & (df_d['EMA-50'] > df_d['EMA-5'])]:
        # You need to assign this column based on your conditions
        df_d['sig'] = 'SELL'


    for i in range(len(df_d)):
        # Check if EMA-50 and EMA-40 are both less than EMA-5
        if df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i] and df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]:
            print(f"Buy condition met at RS: {df_d['EMA-5'].iloc[i]}")
            handle_signal('BUY', df_d['EMA-5'].iloc[i])

        if (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
            print(f"Sell condition 1 met at RS: {df_d['EMA-5'].iloc[i]}")
            close_position('SELL', df_d['EMA-5'].iloc[i])
        elif (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i]):
            print(f"Sell condition 2 met at RS: {df_d['EMA-5'].iloc[i]}")
            close_position('SELL', df_d['EMA-5'].iloc[i])
        elif (df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
            print(f"Sell condition 3 met at RS: {df_d['EMA-5'].iloc[i]}")
            close_position('SELL', df_d['EMA-5'].iloc[i])

    df_d.dropna(inplace=True)

    pd.set_option('display.max_rows', None)
    print(df_d)


get_ema()
