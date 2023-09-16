import ccxt

# Initialize the Phemex exchange object
exchange = ccxt.phemex()

# Define the trading pair for which you want to fetch the order book
symbol = 'BTC/USDT'

# Fetch the order book for the specified trading pair
order_book = exchange.fetch_order_book(symbol)

# Access the bid and ask lists
bids = order_book['bids']  # List of buy orders
asks = order_book['asks']  # List of sell orders

# Print the first few entries in the order book
print("Top 5 bids:")
for bid in bids[:5]:
    print(bid)

print("\nTop 5 asks:")
for ask in asks[:5]:
    print(ask)
