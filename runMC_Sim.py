from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np

#
# Generate portfolios on the "efficient frontier" and tests them. Two portfolios are generated 
# and benchmarked against the SPY. Both have either identical return or identical volatility
# to the SPY in the calibration period.
#
# TODO: Test against random portfolios
#

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
    
    optimalStd = 1.0;
    
    optimalWeight_risk = np.zeros((N_Stocks, 1)) 
    optimalWeight_return = np.zeros((N_Stocks, 1)) 
    
    for i in range(N_MC_Iterations):
        weightVector = np.random.rand(N_Stocks, 1)
        normFactor = np.sum(weightVector)
        weightVector = weightVector / normFactor
        portfolioReturn = np.matmul(ret, weightVector)
        returnAvg[i] = np.average(portfolioReturn)
        returnStd[i] = np.std(portfolioReturn) 
    
        if(returnAvg[i] > 0.99*benchmarkAvg and returnAvg[i] < 1.01*benchmarkAvg):
            if(returnStd[i] < optimalStd):
                optimalWeight_return = weightVector

        if(returnStd[i] > 0.99*benchmarkStd and returnStd[i] < 1.01*benchmarkStd):
            if(returnAvg[i] > benchmarkAvg):
                optimalWeight_risk = weightVector


    #
    # Secondly, evaluate the portfolio in the second half of the year
    #
    print "###" + year + "###"
 
    start_date = year + '-06-01'
    end_date = year + '-12-31' 

    panel_data = data.DataReader(tickers, 'iex', start_date, end_date)  

    close = panel_data['close']
    close = close.fillna(method='ffill')
    returns = close.pct_change(1)
    ret = returns.values
    ret = ret[1:-1, :]

    portfolioReturn_return = np.matmul(ret, optimalWeight_return)
    returnAvg_return = np.average(portfolioReturn_return)
    returnStd_return = np.std(portfolioReturn_return)

    portfolioReturn_risk = np.matmul(ret, optimalWeight_risk)
    returnAvg_risk = np.average(portfolioReturn_risk)
    returnStd_risk = np.std(portfolioReturn_risk)

    benchmark_data = data.DataReader('SPY', 'iex', start_date, end_date)
    benchmark_data = benchmark_data['close']
    benchmark_data = benchmark_data.fillna(method='ffill')
    benchmark_ret = benchmark_data.pct_change(1)
    benchmark_ret = benchmark_ret.values
    benchmark_ret = benchmark_ret[1:-1]
    
    benchmarkAvg = np.average(benchmark_ret)
    benchmarkStd = np.std(benchmark_ret)

    print "{},{},{},{}".format(returnAvg_return, returnStd_return, benchmarkAvg, benchmarkStd) 

    if( (returnAvg_return > benchmarkAvg) and (returnStd_return < benchmarkStd)):
        print "Free lunch!"

    print ' '
    print "{},{},{},{}".format(returnAvg_risk, returnStd_risk, benchmarkAvg, benchmarkStd) 

    if( (returnAvg_risk > benchmarkAvg) and (returnStd_risk < benchmarkStd)):
        print "Free lunch!"
    print "###"

plt.plot(portfolio[:,0], portfolio[:,1], 'bo')
plt.plot(market[:,0], market[:,1], 'ro')
plt.show()
