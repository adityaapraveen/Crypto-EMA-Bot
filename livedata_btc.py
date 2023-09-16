import ccxt
import pandas as pd

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
