import yfinance as yf
import datetime as datetime
import numpy as np
import plotly.graph_objects as go
import random
from dash import dash, dcc, html, Input, Output




# Get the stock data from 50 possible tickers
tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "FB", "TSLA", "NVDA", "JPM", "JNJ", "V",
    "WMT", "MA", "PG", "UNH", "HD", "VZ", "BAC", "DIS", "PYPL", "ADBE", "CMCSA",
    "NFLX", "INTC", "PFE", "KO", "PEP", "CSCO", "ABT", "ABBV", "T", "NKE", "ORCL",
    "MRK", "CRM", "XOM", "IBM", "AMGN", "CVX", "AVGO", "TMO", "MDT", "WFC", "COST",
    "MCD",  "ACN", "QCOM", "HON", "TXN", "PM", "MMM", "GE"
]

'''def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig
'''
# Create the Dash app

app = dash.Dash(__name__, suppress_callback_exceptions = True)

app.layout = html.Div(children=[
    html.H1("Stock Analysis", style ={'text-align': ' center'}),
    dcc.Dropdown(
        id = 'ticker-dropdown',
        options =[{'label': ticker, 'value': ticker} for ticker in tickers],
        value = tickers[0] # set default value
    ),
    html.H2("Stock Price - Past 10 Years"),
    dcc.Graph(id='stock-prices'),
    html.H2("Monte Carlo Simulation - Stock Prices"),
    dcc.Graph(id='monte-carlo-simulation'),
    html.H2("Distribution of Predicted Prices"),
    dcc.Graph(id='histogram')])



#connect the plotly graphs with  dash  components
@app.callback([
    Output(component_id = 'stock-prices', component_property = 'figure'),
    Output(component_id = 'monte-carlo-simulation', component_property = 'figure'),
    Output(component_id = 'histogram', component_property = 'figure'),
    Input(component_id = 'ticker-dropdown', component_property = 'value')
])

def update_graphs(ticker): #argument in this function always refers to component property of input

    end_date = datetime.datetime.today().strftime("%Y-%m-%d")

    # get past 10years of data
    start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * 10)).strftime("%Y-%m-%d")
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    # calculate returns using percent change from previous record
    returns = np.log(1 + stock_data['Close'].pct_change())

    # Define the number of simulations and trading days
    simulations = 500
    trading_days = 50

    # save the simulated prices
    simulated_prices = [0] *  simulations
    for i in range(simulations):
        prices=[0]*(trading_days+1)
        latest_price = stock_data['Close'].iloc[1]
        prices[0] = latest_price
        for j in range(trading_days):
            # choose a random return following a normal distribution of the returns calculated
            random_returns = np.random.normal(returns.mean(), returns.std())
            # exponent of log to return a vlue that can be multiplied
            latest_price = latest_price * np.exp(random_returns)
            prices[j+1]=latest_price

        simulated_prices[i]=prices

    # set dates
    last_date = stock_data.index[-1]
    future_dates = [last_date + datetime.timedelta(days=i) for i in range(trading_days)]

    # create figure simulation for monte carlo simulation
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
        title=f"{ticker} Monte Carlo Simulation - Stock Prices",
        xaxis_title="Date",
        yaxis_title="Price ( USD)"
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



    '''    # check the 90% confidence interval
        expected_price =  round(np.nanmean(last_simulated_prices),2)
        quantile_5 = np.nanpercentile(last_simulated_prices,5)
        quantile_95 = np.nanpercentile(last_simulated_prices,95)'''

    # Create the figure for the histogram
    last_simulated_prices = [sublist[-1] for sublist in simulated_prices]
    fig_histogram = go.Figure(data=[go.Histogram(x=last_simulated_prices, nbinsx=200)])
    fig_histogram.add_vline(x=np.nanpercentile(last_simulated_prices,5), line_dash='dash', line_color = 'firebrick')
    fig_histogram.add_vline(x=np.nanpercentile(last_simulated_prices, 95), line_dash='dash', line_color='firebrick')
    fig_histogram.update_layout(
        title="Distribution of Predicted Prices",
        xaxis_title="Price (USD)",
        yaxis_title="Frequency"


    )
    return fig_stock_prices, fig_monte_carlo, fig_histogram



if __name__ == '__main__':
    app.run_server(debug=True)



