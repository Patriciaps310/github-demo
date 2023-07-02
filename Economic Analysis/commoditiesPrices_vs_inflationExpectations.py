import pandas as pd
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.api import VAR
from sklearn.model_selection import train_test_split
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller

# import csv data from FRED
df_sticky_prices_index = pd.read_csv('STICKCPIM157SFRBATL.csv')
df_oil_prices = pd.read_csv('DCOILWTICO.csv')
df_employment_cost_index = pd.read_csv('ECIALLCIV.csv')

#rename column headers
df_sticky_prices_index = df_sticky_prices_index.\
    rename(columns = {'STICKCPIM157SFRBATL': 'sticky_price_index', 'DATE': 'date'})

df_oil_prices = df_oil_prices.\
    rename(columns = {'DCOILWTICO': 'oil_price', 'DATE': 'date'})

df_employment_cost_index = df_employment_cost_index.\
    rename(columns = {'ECIALLCIV': 'employment_cost', 'DATE': 'date'})

#check data types

'''print(df_sticky_prices_index.dtypes)
print(df_oil_prices.dtypes)
print(df_employment_cost_index.dtypes)'''

# change data types
# there are '.' in certain rows instead of nan
df_oil_prices.loc[df_oil_prices['oil_price'] == '.', 'oil_price'] = np.nan
df_oil_prices['oil_price'] = df_oil_prices['oil_price'].astype(float)
#print(df_oil_prices.dtypes)

# convert date columns to datetime format
df_sticky_prices_index['date'] = pd.to_datetime(df_sticky_prices_index['date'], format = '%Y-%m-%d')
df_oil_prices['date'] = pd.to_datetime(df_oil_prices['date'], format = '%Y-%m-%d')
df_employment_cost_index['date'] = pd.to_datetime(df_employment_cost_index['date'], format = '%Y-%m-%d')

'''print(df_sticky_prices_index.dtypes)
print(df_oil_prices.dtypes)
print(df_employment_cost_index.dtypes)'''



'''#create plots to visualize data

plot_sticky_prices_index = go.Figure()
plot_sticky_prices_index.add_trace(go.Scatter(
    x=df_sticky_prices_index['date'],
    y=df_sticky_prices_index['sticky_price_index'],
    line=dict(color='blue'),
    name='Sticky Prices Index'
))

plot_sticky_prices_index.update_layout(
    title="Sticky Prices Index",
    xaxis_title = "Date",
    yaxis_title = "Index"
)

plot_oil_prices = go.Figure()
plot_oil_prices.add_trace(go.Scatter(
    x=df_oil_prices['date'],
    y=df_oil_prices['oil_price'],
    line=dict(color='blue'),
    name='Oil Price'
))
plot_oil_prices.update_layout(
    title="Sticky Prices Index",
    xaxis_title = "Date",
    yaxis_title = "Price (USD)"
)


plt_employment_cost_index = go.Figure()
plt_employment_cost_index.add_trace(go.Scatter(
    x=df_employment_cost_index['date'],
    y=df_employment_cost_index['employment_cost'],
    line=dict(color='blue'),
    name='Employment Cost Index'
))
plt_employment_cost_index.update_layout(
    title='Employment Cost Index',
    xaxis_title = "Date",
    yaxis_title = "Index"
)


plot_sticky_prices_index.show()
plot_oil_prices.show()
plt_employment_cost_index.show()
'''

# merge all dataframes into one based on date
df_merged = pd.merge(df_sticky_prices_index, df_oil_prices, on='date', how = 'inner')
data= pd.merge(df_merged, df_employment_cost_index, on='date', how = 'inner')

# we want to test oil prices (X)  and their potential impact on prices (Y1) and wages (Y2)
variables = ['oil_price', 'sticky_price_index', 'employment_cost']
data = data.dropna()
data = data[variables]

# split data into training and test data
train, test = train_test_split(data[variables], test_size= 0.2, random_state= 3)

# we will use granger causality before even building a model
# one of the assumptions of granger causality is that the series is stationary
# But let's use Augmented Dickey-Fuller Test to verify

'''
for variable in variables:
    result = adfuller(train[variable])
    print(f'{variable} Test Statistics: {result[0]}')
    print(f'{variable} p-value: {result[1]}')
    print(f'{variable} critical_values: {result[4]}')
    if result[1] > 0.05:
        print(f"{variable} Series is not stationary")
    else:
        print(f"{variable} Series is stationary")
'''

#Since all series are stationary, we can now proceed with granger causality test
# use granger causality test to check if there is any relationship between the series before building a model

max_lag = 12
results_Y1 = grangercausalitytests(train[['oil_price', 'sticky_price_index']], max_lag, verbose=False)





# print p-values and test statistics for each lag order
for lag in range(1, max_lag + 1):
    p_value = results_Y1[lag][0]['ssr_chi2test'][1]
    test_statistic = results_Y1[lag][1][0]
    print(f"Lag Order: {lag} | Test Statistic: {test_statistic} | p-value: {p_value}")


results_Y2 = grangercausalitytests(train[['oil_price', 'employment_cost']], max_lag, verbose=False)
# print p-values and test statistics for each lag order
for lag in range(1, max_lag + 1):
    p_value = results_Y2[lag][0]['ssr_chi2test'][1]
    test_statistic = results_Y2[lag][1][0]
    print(f"Lag Order: {lag} | Test Statistic: {test_statistic} | p-value: {p_value}")



