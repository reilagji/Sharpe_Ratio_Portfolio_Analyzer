import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import re
import numpy as np
pd.set_option('display.float_format','{:.0f}'.format)

st.title("Risk-Adjusted Porfolio Analyzer 🐂")



# ---- SIDEBAR FOR USER INPUTS ------ #
st.sidebar.header("Inputs:")

start_date = st.sidebar.date_input("Start Date:", pd.to_datetime('2020-01-01'))

end_date = st.sidebar.date_input("End Date:", pd.to_datetime('today'),
max_value=pd.to_datetime('today'))
folio_value = st.sidebar.number_input('Enter $ Value of portfolio',min_value=1)

tickers = st.sidebar.text_input("Enter Tickers Seperated by a comma:",placeholder="EG: TSLA,APPL,MSFT")



def relativeret(df):
    pct_change = df.pct_change()
    cumret = (1+pct_change).cumprod() - 1
    cumret = cumret.fillna(0)
    return cumret


#to not throw an error, use iF code similar to excel iferror
if len(tickers) > 0:

    df = relativeret(yf.download(tickers, start_date,end_date)['Close'])
    st.header('Relative Returns of {}'.format(tickers))
    st.line_chart(df)

    changes = yf.download(tickers,start_date,end_date)['Close'].pct_change()
    st.header("Daily Percent Change")
    st.line_chart(changes)
    st.dataframe(changes.describe().transpose())

else: st.text("Enter ticker(s) in the sidebar to see relative returns and daily percent change. \nEnter 2 or more tickers to see asset price correlations and optimal $ allocation\n per company.")


if any("," in ele for ele in tickers) >0:
        st.header("Correlation of Price Action")
        sims = st.sidebar.slider("Select # of simulations to run",min_value=100,max_value=20000)
        fig,ax = plt.subplots()
        plt.style.use("dark_background")
        sns.heatmap(changes.corr(), ax=ax, cmap ="Blues")
        st.write(fig)
else: st.text(" ")


#SHARPE RATIO CALCULATOR

st.header("Optimal Risk-Adjusted Portfolio weightings")

if len(tickers) >0:

    data = yf.download(tickers,start_date,end_date)
    x = data['Close'].pct_change()

    p_weights = []
    p_returns = []
    p_risk = []
    p_sharpe = []

    count = int(sims)
    for k in range(0, count):
        wts = np.random.uniform(size = len(x.columns))
        wts = wts/np.sum(wts)
        p_weights.append(wts)


        mean_ret = (x.mean() * wts).sum()*252
        p_returns.append(mean_ret)


        ret = (x * wts).sum(axis = 1)
        annual_std = np.std(ret) * np.sqrt(252)
        p_risk.append(annual_std)

        sharpe = (np.mean(ret) / np.std(ret))*np.sqrt(252)
        p_sharpe.append(sharpe)


    max_ind = np.argmax(p_sharpe)

    st.text("The Sharpe Ratio for this portfolio is: {}" .format(round(p_sharpe[max_ind],2)))

    st.text("The optimal portfolio allocation per company is: \n{}" .format(np.round(p_weights[max_ind]*folio_value,1)))

    s = pd.Series(p_weights[max_ind]*folio_value, index=x.columns)
    st.bar_chart(s)
else: st.text("A simple introduction to the Sharpe Ratio below.\nSuppose each of these two invesments both returned 40% over the time period.\nSo which was a better investment? Black is much more painful to hold, despite ultimately returning the same % increase.\nSometimes it beat green but other times it severely underperformed.\n This volatility makes it more painful to hold black than green.\n Therefore, in order to evaluate each investment we employ the Sharpe Ratio, which calculates return divivded by volatility experienced.\n The trailing 20-yr sharpe ratio of S&P is roughly 0.45. Therfore, when building a portfolio of stocks we want to aim for a Sharpe Ratio > 0.45 within our portfolio.")
