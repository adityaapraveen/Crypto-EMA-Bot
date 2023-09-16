import pandas as pd
import ccxt
import time

while True:
    try:
        # Initialize the Phemex exchange object
        exchange = ccxt.phemex()

        # Define the symbol you want to fetch data for (BTC/USD in this case)
        symbol = 'BTC/USDT'

        # Fetch the ticker data for the specified symbol
        ticker = exchange.fetch_ticker(symbol)

        # Create a DataFrame from the ticker data
        ticker_df = pd.DataFrame([ticker])

        # Print the DataFrame
        print(ticker_df)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Add a delay (e.g., 10 seconds) to control the fetch rate
    time.sleep(10)  # You need to import the 'time' module for this

# The code will run indefinitely until manually interrupted (e.g., by pressing Ctrl+C)
