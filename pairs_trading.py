import yfinance as yf
import pandas as pd

# Define the ticker symbols for all the stocks in the S&P 500 index
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# Define the start and end date
start_date = '2012-04-23'
end_date = '2022-04-23'

sp500_df = pd.DataFrame()
for ticker in sp500_tickers:
    ticker_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    sp500_df[ticker] = ticker_data['Adj Close']
