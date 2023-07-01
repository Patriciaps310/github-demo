import yfinance as yf
import datetime as datetime
import numpy as np
import plotly.graph_objects as go
import random
from dash import dash, dcc, html



def get_stock_data(ticker):

    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    # get past 10years of data
    start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * 10)).strftime("%Y-%m-%d")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Get the stock data
ticker = input("Enter the ticker symbol: ")
stock_data = get_stock_data(ticker)


'''''
def plot_stock_prices(stock_data, ticker):
    # Build a graph using plotly
    fig = go.Figure()

    # add lines to graph
    fig.add_trace(go.Scatter(
        x=stock_data.index,  # date values
        y=stock_data['Close'],  # closing prices
        name='{} Close'.format(ticker),
        line=dict(color='blue')
    ))

    # add axis labels and titles

    fig.update_layout(
        title= "{} Stock Price - Past 10 Years".format(ticker),
        xaxis_title='Date',
        yaxis_title='Price (USD)'
    )

    fig.show()
'''

# Define the number of simulations and trading days
simulations = 1000
trading_days = 252

def monte_carlo_simulation(stock_data, simulations, trading_days):
    # calculate returns using percent change from previous record
    returns = np.log(1 + stock_data['Close'].pct_change())

    # save the simulated prices
    simulated_prices = []
    for i in range(simulations):
        prices = [stock_data['Close'].iloc[1]]
        for j in range(trading_days):
            # choose a random return following a normal distribution of the returns calculated
            random_returns = np.random.normal(returns.mean(), returns.std())
            # exponent of log to return a vlue that can be multiplied
            price = prices[-1] * np.exp(random_returns)
            prices.append(price)

        simulated_prices.append(prices)
    return simulated_prices

simulated_prices = monte_carlo_simulation(stock_data, simulations, trading_days)

'''
def plot_monte_carlo_simulation(simulated_prices, trading_days):

    #Build a graph using plotly
    fig = go.Figure()

    # Calculate future dates
    last_date = stock_data.index[-1]
    future_dates = [last_date + datetime.timedelta(days=i) for i in range(trading_days)]


    #add lines to graph on top of each other for each iteration
    for i in range(simulations):
        # choose a random color
        color = f"rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})"
        fig.add_trace(go.Scatter(
            x= future_dates, #date values
            y= simulated_prices[i], #simulated closing prices
            line = dict(color=color),
            showlegend=False  # Remove legend for each trace

        ))


    # add axis labels and titles

    fig.update_layout(
        title = f"Monte Carlo Simulation - Stock Prices",
        xaxis_title='Date',
        yaxis_title = 'Price (USD)'
    )
    fig.show()
'''

def calculate_confidence_intervals(simulated_prices):
    # create a list only with the predict values in a year from now
    last_simulated_prices = [sublist[-1] for sublist in simulated_prices]

    # check the 90% confidence interval
    expected_price =  round(np.nanmean(last_simulated_prices),2)
    quantile_5 = np.nanpercentile(last_simulated_prices,5)
    quantile_95 = np.nanpercentile(last_simulated_prices,95)
    return last_simulated_prices

last_simulated_prices = calculate_confidence_intervals(simulated_prices)

'''
def plot_price_histogram(last_simulated_prices):
    # Create a histogram to show confidence interval of results
    plt.hist(last_simulated_prices, bins=200)
    # add vertical line with 5% and 95% threshold
    plt.axvline(np.nanpercentile(last_simulated_prices,5), color='r', linestyle='dashed', linewidth=1)
    plt.axvline(np.nanpercentile(last_simulated_prices,95), color='r', linestyle='dashed', linewidth=1)
    plt.show()
'''

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







last_date = stock_data.index[-1]
future_dates = [last_date + datetime.timedelta(days=i) for i in range(trading_days)]

#create figure simulation for monte carlo simulation
fig_monte_carlo = go.Figure()
for i in range(simulations):
    # choose a random color
    color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
    fig_monte_carlo.add_trace(go.Scatter(
        x=future_dates,  # date values
        y=simulated_prices[i],  # simulated closing prices
        line=dict(color=color),
        showlegend=False  # Remove legend for each trace

    ))

fig_monte_carlo.update_layout(
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


# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Stock Analysis"),
    html.H2(f"{ticker} Stock Price - Past 10 Years"),
    dcc.Graph(id='stock-prices', figure=fig_stock_prices),
    html.H2("Monte Carlo Simulation - Stock Prices"),
    dcc.Graph(id='monte-carlo-simulation', figure=fig_monte_carlo),
    html.H2("Distribution of Predicted Prices"),
    dcc.Graph(id='histogram', figure= fig_histogram)])


if __name__ == '__main__':
    app.run_server(debug=True)