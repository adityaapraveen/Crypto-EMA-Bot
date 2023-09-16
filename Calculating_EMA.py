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

def get_ema():
    
    print("STARTING INDICATORS...")

    timeframe = '1d'
    num_bars = 100

    bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_bars)

    df_d = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

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

    for i in range(1, len(df_d)):
        ema5.append((df_d['close'][i] * 2 / (period5 + 1)) + (ema5[i - 1] * (1 - 2 / (period5 + 1))))

    df_d['EMA-5'] = ema5

    for i in range(1, len(df_d)):
        ema40.append((df_d['close'][i] * 2 / (period40 + 1)) + (ema40[i - 1] * (1 - 2 / (period40 + 1))))

    df_d['EMA-40'] = ema40

    for i in range(1, len(df_d)):
        ema50.append((df_d['close'][i] * 2 / (period50 + 1)) +
                    (ema50[i - 1] * (1 - 2 / (period50 + 1))))
    df_d['EMA-50'] = ema50

    # stop-loss percentage (1%)
    stop_loss_percent = 0.01

    for i in range(len(df_d)):
    #     # Calculate the stop-loss price based on the entry price
    #     entry_price = df_d['EMA-5'].iloc[i]
    #     stop_loss_price = entry_price * (1 - stop_loss_percent)

    #     # Calculate the take-profit price based on the entry price  
    #     take_profit_price = entry_price * (1 + target / 100)

    #     # Check if the current low price breaches the stop-loss price
    #     if df_d['low'].iloc[i] <= stop_loss_price:
    #         print(f"Stop loss triggered at RS: {df_d['EMA-5'].iloc[i]}")
    #         # Place limit sell order logic here for stop loss

        # Check active positions for stop-loss condition
        for position in active_positions:
            entry_price, stop_loss_price = position
            # Check if the current low price breaches the stop-loss price
            if df_d['low'].iloc[i] <= stop_loss_price:
                print(f"Stop loss triggered at RS: {df_d['EMA-5'].iloc[i]}")
                # Place limit sell order logic here for stop loss
                active_positions.remove(position)  # Remove the closed position

        # Check if EMA-50 and EMA-40 are both less than EMA-5
        # if df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i] and df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]:
        #     print(f"Buy condition met at RS: {df_d['EMA-5'].iloc[i]}")
            # Place limit buy order logic here
            # Example: phemex.create_limit_buy_order(symbol, pos_size, limit_buy_price)

        # if (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
        #     print(f"Sell condition 1 met at RS: {df_d['EMA-5'].iloc[i]}")
        # elif (df_d['EMA-40'].iloc[i] > df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] < df_d['EMA-5'].iloc[i]):
        #     print(f"Sell condition 2 met at RS: {df_d['EMA-5'].iloc[i]}")
        # elif (df_d['EMA-40'].iloc[i] < df_d['EMA-5'].iloc[i]) and (df_d['EMA-50'].iloc[i] > df_d['EMA-5'].iloc[i]):
        #     print(f"Sell condition 3 met at RS: {df_d['EMA-5'].iloc[i]}")

    # df_d.loc[df_d['EMA-20'] and df_d['EMA-30'] > df_d['EMA-5'], 'sig'] = 'SELL'   26320 26619
    # df_d.loc[df_d['EMA-20'] and df_d['EMA-30'] < df_d['EMA-5'], 'sig'] = 'BUY'
    df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) & (df_d['EMA-50'] > df_d['EMA-5']), 'sig'] = 'SELL'
    df_d.loc[(df_d['EMA-40'] < df_d['EMA-5']) & (df_d['EMA-50'] < df_d['EMA-5']), 'sig'] = 'BUY'

    # if EMA-5 is in between EMA-40 and EMA-50

    df_d.loc[(df_d['EMA-40'] > df_d['EMA-5']) & (df_d['EMA-50'] < df_d['EMA-5']), 'sig'] = 'SELL'
    df_d.loc[(df_d['EMA-40'] < df_d['EMA-5']) & (df_d['EMA-50'] > df_d['EMA-5']), 'sig'] = 'SELL'


    # df_d.loc[(df_d['EMA-40'] > df_d['EMA-5'] > df_d['EMA-50']), 'sig'] = 'SELL-L'
    # df_d.loc[(df_d['EMA-50'] > df_d['EMA-5'] > df_d['EMA-40']), 'sig'] = 'SELL-L'
    # df_d = df_d[df_d['sig'].notna() | df_d['sig'].isna().cumsum().eq(1)]

    df_d.dropna(inplace=True)

    pd.set_option('display.max_rows', None)
    print(df_d)
    return df_d

df_d = get_ema()


# Initialize trade direction flag
current_direction = 'none'  # 'none' indicates no active trade


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
                # ema = min(df_d['EMA-40'].iloc[i], df_d['EMA-50'].iloc[i])
                # pro = df_d['EMA-5'].iloc[i] - ema
                # print(f"profit made:{pro}")
                # Place your limit sell order logic for condition 1 here
                # phemex.create_limit_sell_order(symbol, pos_size, price, params)
                open_pos = False  # Set the open_pos flag to False after selling

bot(df_d)


