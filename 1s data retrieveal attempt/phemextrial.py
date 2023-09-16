





# Deadend phemex doesnt provide 1 second interval data





import requests
endpoint = 'https://api.phemex.com'
symbol = 'BTC/USDT'
interval = '1s'
limit = 1000
url = f'{endpoint}/md/tickers/history'

params = {
    'symbol': symbol,
    'interval': interval,
    'limit': limit
}
response = requests.get(url, params=params)
kline_data = response.json()