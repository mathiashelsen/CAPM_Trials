from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np


tickers = ['AAPL', 'JNJ', 'JPM', 'XOM', 'V', 'PG', 'BA', 'CSCO', 'UNH']
#, 'JNJ', 'JPM', 'GOOG', 'GOOGL','XOM', 'V', 'PG', 'BAC', 'CSCO', 'VZ', 'UNH', 'DIS', 'T', 'PFE', 'CVX', 'MA', 'HD', 'MRK', 'INTC', 'CMCSA', 'KO', 'WFC', 'BA', 'PEP', 'C']


years = ['2015', '2016', '2017', '2018']

market = np.zeros((len(years), 2))
portfolio = np.zeros((len(years), 2))

for j in range(len(years)):
    year = years[j]
    #
    # First, generate the optimal portfolio based on information on the first half of the year
    #

    start_date = year + '-01-01'
    end_date = year + '-06-01'
    
    panel_data = data.DataReader(tickers, 'iex', start_date, end_date)
    close = panel_data['close']
    close = close.fillna(method='ffill')
    returns = close.pct_change(1)
    ret = returns.values
    ret = ret[1:-1, :]
    
    benchmark_data = data.DataReader('SPY', 'iex', start_date, end_date)
    benchmark_data = benchmark_data['close']
    benchmark_data = benchmark_data.fillna(method='ffill')
    benchmark_ret = benchmark_data.pct_change(1)
    benchmark_ret = benchmark_ret.values
    benchmark_ret = benchmark_ret[1:-1]
    
    benchmarkAvg = np.average(benchmark_ret)
    benchmarkStd = np.std(benchmark_ret)
    
    N_MC_Iterations = 10000
    N_Stocks = np.size(ret, 1)
    
    returnAvg = np.zeros((N_MC_Iterations, 1));
    returnStd = np.zeros((N_MC_Iterations, 1));
    
    optimalWeights = np.zeros((N_Stocks, 1));
    optimalStd = 1.0;
    
    for i in range(N_MC_Iterations):
        weightVector = np.random.rand(N_Stocks, 1)
        normFactor = np.sum(weightVector)
        weightVector = weightVector / normFactor
        portfolioReturn = np.matmul(ret, weightVector)
        returnAvg[i] = np.average(portfolioReturn)
        returnStd[i] = np.std(portfolioReturn) 
    
        if(returnAvg[i] > 0.99*benchmarkAvg and returnAvg[i] < 1.01*benchmarkAvg):
            if(returnStd[i] < optimalStd):
                optimalWeight = weightVector
                optimalStd = returnStd[i]
                optimalAvg = returnAvg[i]
    print "###"
    print "{},{},{},{}".format(optimalAvg[0], optimalStd[0], benchmarkAvg, benchmarkStd) 

    #
    # Secondly, evaluate the portfolio in the second half of the year
    #
 
    start_date = year + '-06-01'
    end_date = year + '-12-31' 

    panel_data = data.DataReader(tickers, 'iex', start_date, end_date)  

    close = panel_data['close']
    close = close.fillna(method='ffill')
    returns = close.pct_change(1)
    ret = returns.values
    ret = ret[1:-1, :]

    portfolioReturn = np.matmul(ret, weightVector)
    returnAvg = np.average(portfolioReturn)
    returnStd = np.std(portfolioReturn)

    benchmark_data = data.DataReader('SPY', 'iex', start_date, end_date)
    benchmark_data = benchmark_data['close']
    benchmark_data = benchmark_data.fillna(method='ffill')
    benchmark_ret = benchmark_data.pct_change(1)
    benchmark_ret = benchmark_ret.values
    benchmark_ret = benchmark_ret[1:-1]
    
    benchmarkAvg = np.average(benchmark_ret)
    benchmarkStd = np.std(benchmark_ret)

    market[j,0] = benchmarkStd
    market[j,1] = benchmarkAvg

    portfolio[j,0] = returnStd
    portfolio[j,1] = returnAvg

    print "{},{},{},{}".format(returnAvg, returnStd, benchmarkAvg, benchmarkStd) 
    print returnAvg - benchmarkAvg
    print returnStd - benchmarkStd
    print "###"

plt.plot(portfolio[:,0], portfolio[:,1], 'bo')
plt.plot(market[:,0], market[:,1], 'ro')
plt.show()
