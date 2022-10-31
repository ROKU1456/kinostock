import mplfinance as mpf
from pandas_datareader import data
import warnings
warnings.simplefilter('ignore')
import streamlit as st
import pandas as pd
import datetime
import pytz
st.set_option('deprecation.showPyplotGlobalUse', False)
import yfinance as yf

# Sidebar
st.sidebar.subheader('Query parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.datetime.now(pytz.timezone('Asia/Tokyo')))

# Retrieving tickers data
ticker_list = pd.read_csv('constituents_symbols.csv')
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol

#Title
tickerData = yf.Ticker(tickerSymbol) # Get ticker data
string_name = tickerData.info['longName']
st.header('**%s**' % string_name)

df = data.DataReader(tickerSymbol, 'yahoo', start_date, end_date)

mpf.plot(df, type='candle',figsize=(30,10),style='yahoo')
#style='classic', 'yahoo', 'charles', 'mike', 'starsandstripes'などで見た目が変えられる

#出来高を追加
mpf.plot(df, type='candle', figsize=(30,10), style='starsandstripes',volume=True)

#ボリンジャーバンドの追加
import talib as ta
df['upper'], df['middle'], df['lower'] = ta.BBANDS(df['Adj Close'],timeperiod=25, nbdevup=2, nbdevdn=2, matype=0)
#matype 0:単純移動平均、1:指数移動平均、2:加重移動平均

#mpfinanceでデフォルｙとで認識できるのはopen, high, low, close, volumeだけ
#それ以外はmake_addplotでメソッドを追加する
apds = [mpf.make_addplot(df['upper'], color='g'),
        mpf.make_addplot(df['middle'], color='b'),
        mpf.make_addplot(df['lower'], color='r')
       ]

mpf.plot(df, type='candle', figsize=(30,10), style='yahoo', volume=True, addplot=apds)

#MACD用のdf追加
df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(df['Adj Close'],fastperiod=12,slowperiod=26, signalperiod=9)

apds = [mpf.make_addplot(df['upper'], color='g'),
        mpf.make_addplot(df['middle'], color='b'),
        mpf.make_addplot(df['lower'], color='r'),
        mpf.make_addplot(df['macdhist'], type='bar', color='gray', width=1.0, panel=1, alpha=0.5, ylabel='MACD')
       ]

mpf.plot(df, type='candle', figsize=(30,10), style='yahoo', volume=True, addplot=apds,
        volume_panel=2, panel_ratios=(3,1,1))   #出来高を表示する順番＝2、グラフの大きさの比率は3:1:1

#RSIの追加
df['RSI'] = ta.RSI(df['Adj Close'], timeperiod=25)

apds = [mpf.make_addplot(df['upper'], color='g'),
        mpf.make_addplot(df['middle'], color='b'),
        mpf.make_addplot(df['lower'], color='r'),
        mpf.make_addplot(df['macdhist'], type='bar', color='gray', width=1.0, panel=1, alpha=0.5, ylabel='MACD'),
        mpf.make_addplot(df['RSI'], panel=2, type='line', ylabel='RSI')
       ]

arr = mpf.plot(df, type='candle', figsize=(15,10), style='yahoo', volume=True, addplot=apds,
        volume_panel=3, panel_ratios=(5,2,2,1))   #出来高を表示する順番＝2、グラフの大きさの比率は3:1:1

#fig, ax = mpf.subplots()
#ax.hist(arr, bins=20)
st.pyplot(arr)