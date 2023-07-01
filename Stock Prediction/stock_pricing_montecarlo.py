import yfinance as yf
import pandas as pd
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import random


# get past 10years of data
end_date = datetime.datetime.today().strftime("%Y-%m-%d")
start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * 10)).strftime("%Y-%m-%d")

# get data from yahoo finance. Just for microsoft as a test
stock_data= yf.download('MSFT', start=start_date, end=end_date)

#Build a graph using plotly
fig = go.Figure()

#add lines to graph
fig.add_trace(go.Scatter(
    x= stock_data.index, #date values
    y=stock_data['Close'], #closing prices
    name = 'MSFT Close',
    line= dict(color='blue')
))

# add axis labels and titles

fig.update_layout(
    title = f"MSFT Stock Price - Past 10 Years",
    xaxis_title='Date',
    yaxis_title = 'Price (USD)'
)

#fig.show()


# Simulation of random walk to try to predict future values

# calculate returns using percent change from previous record
returns = stock_data['Close'].pct_change()

# calculate volatility of returns
volatility = returns.std()

# there are 252 trading days in a year
trading_days = 252

# set the number of monte carlo simulations we want
simulations = 1000

# save the simulated prices
simulated_prices = []
last_prices_simulated = []
for i in range(simulations):
    prices = []
    for j in range(trading_days):
        if j == 0:
            #set initial price as the actual price from the last day of our data
            prices.append(stock_data['Close'].iloc[1])
        else:
            # data a random value given the prices changes previously calculate.
            # Every new simulated prices is calculated on top of he previously calculated random value
            prices.append(prices[j-1]*(1+np.random.choice(returns)))
    simulated_prices.append(prices)

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


# create a list only with the predict values in a year from now
last_simulated_prices = [sublist[-1] for sublist in simulated_prices]

# check the 90% confidence interval
print("Expected price: ", round(np.nanmean(last_simulated_prices),2))
print("Quantile (5%): ",np.nanpercentile(last_simulated_prices,5))
print("Quantile (95%): ",np.nanpercentile(last_simulated_prices,95))

# Create a histogram to show confidence interval of results
plt.hist(last_simulated_prices, bins=200)
# add vertical line with 5% and 95% threshold
plt.axvline(np.nanpercentile(last_simulated_prices, 5), color='r', linestyle='dashed', linewidth=1)
plt.axvline(np.nanpercentile(last_simulated_prices, 95), color='r', linestyle='dashed', linewidth=1)
plt.show()






