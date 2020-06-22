import pandas as pd
import numpy as np
import os
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import matplotlib.cm as cm
from pandas.plotting import register_matplotlib_converters
from pandas.tseries.offsets import DateOffset, BDay

def FanChart(FileSeries, ForecastDays, TailSize):

    percentiles = [0.5,2.5,12.5,25.0,50,75.0,87.5,97.5,99.5]
    probabilities = ['Probabilities']

    for i in range(len(percentiles)):
        prob = percentiles[len(percentiles)-1-i] - percentiles[i]
        if prob > 0:
            probabilities.append(str(prob) + '%')

    colormap = cm.Blues
    basecolor = colormap(0.9)
    color1 = colormap(0.25)
    color2 = colormap(0.4)
    color3 = colormap(0.5)
    colors = [color1,color2,color3,basecolor,basecolor,color3,color2,color1]
    
    curdirectory = str(os.path.dirname(os.path.realpath(__file__))) + '\\'
    file = curdirectory + FileSeries + '.csv'

    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
    df['Date'] = pd.to_datetime(df['Date'])
    lastdate = df['Date'].max()
    x = df.tail(1)
    lastvalue = float(x['Close'])

    rows_list = []
    cols = ['Date','Close']
    for j in percentiles:
        cols.append('p_' + str(j))
        
    df0 = pd.DataFrame(columns=cols)
    df0['Date'] = df['Date']

    for j in cols:
        if j != 'Date':
            df0[j] = df['Close']

    for i in range(ForecastDays):
        
        k = i + 1
        df['pct_'+ str(k) + 'd'] = 1 + df['Close'].pct_change(k)
        results = []
        result = pd.to_datetime(lastdate) + pd.offsets.BDay(k)
        results.append(result)
        results.append(lastvalue)

        for j in percentiles:
            p = np.nanpercentile(df['pct_' + str(k) +'d'], j) * lastvalue
            results.append(p)

        rows_list.append(results)
    
    df2 = pd.DataFrame(rows_list, columns=cols)
    df3 = pd.concat([df0,df2])
    df3['Date'] = pd.to_datetime(df3['Date'])
    df3.reset_index()
    df3.sort_values(by='Date', ascending=False)
    df3 = df3.tail(TailSize)

    plt.figure(figsize=(10,6))
    axes = plt.gca()
    plt.plot(df3['Date'],df3['Close'], color = basecolor, lw=0.8)

    i = 0
    limit = len(percentiles) - 1

    while True:
        lower = percentiles[i]
        upper = percentiles[i+1]
        plt.fill_between(df3['Date'], df3['p_' + str(lower)], df3['p_' + str(upper)], color =  colors[i], lw=0.7)
        i = i + 1
        if i == limit:
            break

    custom_lines = [Line2D([0],[0], color = 'white', lw = 6),
                    Line2D([0],[0], color = color1, lw = 6),
                    Line2D([0],[0], color = color2, lw = 6),
                    Line2D([0],[0], color = color3, lw = 6),
                    Line2D([0],[0], color = basecolor, lw = 6)]
    axes.legend()
    axes.legend(custom_lines,probabilities, loc="lower left")
    chartTitle = FileSeries + ' spot rate forecast distribution for ' + str(ForecastDays) + ' days'
    plt.title(chartTitle)
    plt.show()


if __name__ == '__main__':

    register_matplotlib_converters()
    pd.options.mode.chained_assignment = None

    FanChart('GBPUSD',60, 350)