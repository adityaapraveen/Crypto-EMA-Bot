''' this bot is a short bot'''

import ccxt
import pandas as pd 
import numpy as np 
from datetime  import date, datetime #timezone, tzinfo
import time, schedule

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': '386e3334-a2d4-4afe-aa9e-6ebb9ca03496',
    'secret': 'NCjyzzzMgtUBbUFKbRqHD_C4dzvkFw-HrGbV3JeiVKUxNzQxYjg4NC05NDUyLTRjNzEtYWU3NC04OWJjOGU3ZDY1MDA'
})

# To check if im connected
# print(phemex.fetch_balance())

symbol = 'uBTCUSD'
pos_size = 50
params = {'timeInForce': 'PostOnly',}
target = 25


def ask_bid():  # ask_bid()[0] = ask, [1] = bid

    ob = phemex.fetch_order_book(symbol)
    # print(ob)
    bid = ob['bids'][0][0]
    ask = ob['asks'][0][0]

    return ask, bid  #ask_bid()[0] = ask, [1] = bid

#print(ask_bid())

# Find daily SMA 20

def daily_sma():
    print("STARTING INDICATORS...")

    timeframe = '1d'
    num_bars = 100

    bars = phemex.fetch_ohlcv(symbol, timeframe = timeframe, limit = num_bars)
    df_d = pd.DataFrame(bars, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    df_d['timestamp'] = pd.to_datetime(df_d['timestamp'], unit = 'ms')

    # Daily SMA - 20 day
    df_d['sma20_d'] = df_d.close.rolling(20).mean()

    # if the BID < 20 day SMA then = BEARISH, if the BIF > 20 day SMA then = BULLISH
    
    bid = ask_bid()[1]
    # bid = 40000

    # if SMA > bid = SELL, if SMA < bid = BUY
    df_d.loc[df_d['sma20_d'] > bid, 'sig'] = 'SELL'
    df_d.loc[df_d['sma20_d'] < bid, 'sig'] = 'BUY'


    # if bid < df_d['sma20_d']:
    #     print("bearish...")
    # else:
    #     print("bullish...")
    # print(df_d)

    return df_d
# daily_sma()
# Find 15min SMA 20


def f15_sma():
    print("STARTING 15min SMA...")

    timeframe = '15m'
    num_bars = 100

    bars = phemex.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_bars)
    df_f = pd.DataFrame(
        bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    df_f['timestamp'] = pd.to_datetime(df_f['timestamp'], unit='ms')

    # Daily SMA - 20 day
    df_f['sma20_15m'] = df_f.close.rolling(20).mean()


    # buy price 1+2 and sell price 1+2 (then later figure out which to choose)
    # buy/sell to open around the 15m sma (20day) - .1% under and .3% over
    df_f['bp_1'] = df_f['sma20_15m'] * 1.001  # 15m sma .1% under and .3% over
    df_f['bp_2'] = df_f['sma20_15m'] * .997
    df_f['sp_1'] = df_f['sma20_15m'] * .999
    df_f['sp_2'] = df_f['sma20_15m'] * 1.003

    # figure out if buy or sell to open
    # df_d = daily_sma()
    # sig = df_d.iloc[-1]['sig']
    # # print(sig)

    # df_f.loc[df_f['sma20_d'] > sig, 'sig'] = 'SELL'
    # df_f.loc[df_f['sma20_d'] < sig, 'sig'] = 'BUY'


    # if sig == 'SELL':
    #     print("We should be opening as a sell")
    #     open_as_buy = False
    #     df_f['sig'] = 'SELL'

    # else:
    #     print("We should be opening as buy")
    #     open_as_buy = True
    #     df_f['sig'] = 'BUY'


    # print(df_f)


    return df_f
# f15_sma()

# df_d = daily_sma()
# df_f = f15_sma()
# ask = ask_bid()[0]
# bid = ask_bid()[1]

#combining the dataframes

# print(df_d)
# print(df_f)



# determine the trend
# if the BID < 20 day SMA then = BEARISH, if the BIF > 20 day SMA then = BULLISH



# Strategy - determine the trend with 20 day sma
# then based off of the trend to open (short/long) around the 15min SMA (20day)
#Entry
#EXIT

def open_positions():
    params = {'type':'swap', 'code':'USD'}
    phe_bal = phemex.fetch_balance(params = params)
    open_positions = phe_bal['info']['data']['positions']
    #print(open_positions)
    openpos_side = open_positions[0]['side']
    openpos_size = open_positions[0]['size']

    if openpos_side == ('Buy'):
        openpos_bool = True
        long = True
    elif openpos_side == ('Sell'):
        openpos_bool = True
        long = False
    else:
        openpos_bool = False
        long = None

    return open_positions, openpos_bool, openpos_size, long

# open_positions()


def kill_switch():

    # will limit close us
    print("Starting the kill switch")
    openpos =   open_positions()[1] #truw or false
    long = open_positions()[3]
    kill_size = open_positions()[2]

    print(f"openposition: {openpos}  long: {long}  size: {size}")

    while openpos == True:
        print("starting kill switch loop till limit fill")
        temp_df = pd.DataFrame()
        print("just made a temp df")

        phemex.cancel_all_orders(symbol)
        openpos = open_positions()[1]
        long = open_positions()[3]
        kill_size = open_positions()[2]
        kill_size = int(kill_size)

        ask = ask_bid()[0]
        bid = ask_bid()[1]

        if long == False:
            phemex.create_limit_buy_order(symbol, kill_size, params)
            print(f"just made a BUY to CLOSE order of {kill_size} {symbol} at ${bid}")
            print("sleeping for 30secs to see if it fills")
            time.sleep(30)
        elif long == True:
            phemex.create_limit_sell_order(symbol, kill_size, ask, params)
            print(f"just made a SELL to CLOSE order of {kill_size} {symbol} at ${ask}")
            print("sleeping for 30secs to see if it fills")
            time.sleep(30)
        else:
            print("--------something i didnt expect in killswitch--------")

        openpos = open_positions()[1]


# kill_switch()


# onl_close() [0] pnlclose and [1] is in_pos  [2] is size and [3] is long
def pnl_close():

    # if hit target then close
    print("checking to see if its time to exit...")


    params = {'type':'swap', 'code':'USD'}
    pos_dict = phemex.fetch_positions(params=params)
    #print(pos_dict)
    pos_dict = pos_dict[0]
    side = pos_dict['side']
    size = pos_dict['contracts']
    entry_price = float(pos_dict['entryPrice'])
    leverage = float(pos_dict['leverage'])

    current_price = ask_bid()[1]

    print(f"side: {side}  |  entry_price: {entry_price}  |  lev: {leverage}")

    # short or long

    if side == 'long':
        diff = current_price - entry_price
        long = True
    else:
        diff = entry_price - current_price
        long = False
    try:
        perc = round(((diff/entry_price) * leverage), 10)
    except:
        perc = 0

    # print(f"diff: {diff} | perc: {perc}")

    perc = 100 * perc
    print(f"This is our PNL percentage: {(perc)}%")

    pnlclose = False
    in_pos = False

    if perc > 0:
        # in_pos = True

        print("We are in a WINNING position")
        if perc > target:
            print(f"starting kill switch because we hit our target of {target}%")    
            pnclose = True
            kill_switch()  
        else:
            #this is where i should put my stoploss, but im using position size as my stoploss

            print("we have not hit our target yet")

    elif perc < 0:
        print("we are in a losing position but holding on")
        in_pos = True


    else:
        print("we are not in position")

    print("just finished checking PNL close")

    return pnlclose, in_pos, size, long

    #return in_pos 

# pnl_close()


def bot():

    pnl_close()  #checking if we hit out pnl

    df_d = daily_sma() # determines LONG/SHORT
    df_f = f15_sma()   # provides prices bp_1, bp_2, sp_1, sp_2
    ask = ask_bid()[0] #
    bid = ask_bid()[1]

    # MAKE OPEN ORDER
    # LONG or SHORT?
    sig = df_d.iloc[-1]['sig']
    #print(sig)
    open_size = pos_size / 2

    # ONLY RUN IF NOT IN POSITION 
    # in_pos = True

    in_pos = pnl_close()[1]
    if in_pos == False:
        
        if sig == 'BUY':
            print("Making an opening order as a BUY")
            bp_1 = df_f.iloc[-1]['bp_1']
            bp_2 = df_f.iloc[-1]['bp_2']
            print(f"this is bp_1: {bp_1} this is bp_2: {bp_2}")
            phemex.create_limit_buy_order(symbol, open_size, bp_1, params)
            phemex.create_limit_buy_order(symbol, open_size, bp_2, params)
            print("just made opening order so going to sleep for 2 mins")

            time.sleep(120)
        else:
            print("Making an opening order as a SELL")
            sp_1 = df_f.iloc[-1]['sp_1']
            sp_2 = df_f.iloc[-1]['sp_2']
            print(f"this is sp_1: {sp_1} this is sp_2 {sp_2}")
            phemex.create_limit_sell_order(symbol, open_size, sp_1, params)
            phemex.create_limit_sell_order(symbol, open_size, sp_2, params)

            print("just made opening order so going to sleep for 2 mins")
            time.sleep(120)

    else:
        print("we are in position already so not making new orders")

# bot()

schedule.every(28).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
    except:
        print("+++++ MAYBE AN INTERNET PROB OR SOMETHING")
        time.sleep(30)

#Get BID and ASK
