import yfinance as yf
import datetime as datetime
import numpy as np
import plotly.graph_objects as go
import random
from dash import dash, dcc, html, Input, Output



def get_stock_data(ticker):
    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * 10)).strftime("%Y-%m-%d")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


# Prompt the user to enter the ticker symbol
ticker = input("Enter the ticker symbol: ")

# Get the stock data
stock_data = get_stock_data(ticker)

# Calculate the returns
returns = np.log(1 + stock_data['Close'].pct_change())

# Set the number of simulations and trading days
num_simulations = 1000
num_trading_days = 252

# Perform the Monte Carlo simulation
simulated_prices = []
for i in range(num_simulations):
    prices = [stock_data['Close'].iloc[-1]]
    for _ in range(num_trading_days):
        random_return = np.random.choice(returns)
        price = prices[-1] * np.exp(random_return)
        prices.append(price)
    simulated_prices.append(prices)

# Calculate future dates
last_date = stock_data.index[-1]
future_dates = [last_date + datetime.timedelta(days=i) for i in range(num_trading_days)]

# Create the figure for the Monte Carlo simulation graph
fig_simulation = go.Figure()
for i in range(num_simulations):
    color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
    fig_simulation.add_trace(go.Scatter(
        x=future_dates,
        y=simulated_prices[i],
        line=dict(color=color),
        showlegend=False
    ))
fig_simulation.update_layout(
    title="Monte Carlo Simulation - Stock Prices",
    xaxis_title="Date",
    yaxis_title="Price (USD)"
)

# Create the figure for the histogram
last_simulated_prices = [sublist[-1] for sublist in simulated_prices]
fig_histogram = go.Figure(data=[go.Histogram(x=last_simulated_prices, nbinsx=200)])
fig_histogram.update_layout(
    title="Distribution of Predicted Prices",
    xaxis_title="Price (USD)",
    yaxis_title="Frequency"
)

# Create the figure for the historical stock prices
fig_stock_prices = go.Figure()
fig_stock_prices.add_trace(go.Scatter(
    x=stock_data.index,
    y=stock_data['Close'],
    line=dict(color='blue'),
    name='Historical Stock Prices'
))
fig_stock_prices.update_layout(
    title=f"{ticker} Stock Price - Past 10 Years",
    xaxis_title="Date",
    yaxis_title="Price (USD)"
)

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Stock Analysis"),
    html.H2(f"{ticker} Stock Price - Past 10 Years"),
    dcc.Graph(id='stock-prices', figure=fig_stock_prices),
    html.H2("Monte Carlo Simulation - Stock Prices"),
    dcc.Graph(id='monte-carlo-simulation', figure=fig_simulation),
    html.H2("Distribution of Predicted Prices"),
    dcc.Graph(id='histogram', figure=fig_histogram)
])

if __name__ == '__main__':
    app.run_server(debug=True)