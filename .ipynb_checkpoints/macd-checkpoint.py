import streamlit as st
import pandas as pd
from pandas_datareader import data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import mplfinance as mpf
import warnings
warnings.simplefilter('ignore')
import datetime
import pytz
st.set_option('deprecation.showPyplotGlobalUse', False)
import cufflinks as cf
import numpy as np

# Sidebar
st.sidebar.subheader('Query parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.datetime.now(pytz.timezone('Asia/Tokyo')))

# Retrieving tickers data
ticker_list = pd.read_csv('constituents_symbols.csv')
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol
tickerData = yf.Ticker(tickerSymbol) # Get ticker data

df = data.DataReader(tickerSymbol, 'yahoo', start_date, end_date)
#df = data.DataReader(tickerSymbol, 'yahoo', start_date, end_date)
#d_all = pd.date_range(start=df['datetime'].iloc[0],end=df['datetime'].iloc[-1])
#d_obs = [d.strftime("%Y-%m-%d") for d in df['datetime']]
#d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs]

# figを定義
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.2, 0.7], x_title="Date")

# indexに指定されている"Date"を使用するためindex指定解除
df =df.reset_index()

# Candlestick 
fig.add_trace(
    go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="OHLC"),
    row=1, col=1
)

# Volume
fig.add_trace(
    go.Bar(x=df["Date"], y=df["Volume"], name="Volume"),
    row=2, col=1
)

def macd(df):
    FastEMA_period = 12  # 短期EMAの期間
    SlowEMA_period = 26  # 長期EMAの期間
    SignalSMA_period = 9  # SMAを取る期間
    df["MACD"] = df["Close"].ewm(span=FastEMA_period).mean() - df["Close"].ewm(span=SlowEMA_period).mean()
    df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
    return df
 
# MACDを計算する
df = macd(df)

fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD", mode="lines"), row=3, col=1)
fig.add_trace(go.Scatter(x=df["Date"], y=df["Signal"], name="Signal", mode="lines"), row=3, col=1)

df["SMA5"] = df["Close"].rolling(window=5).mean()
df["SMA25"] = df["Close"].rolling(window=25).mean()

# SMA5 と SMA25の差分を計算する
diff = df["SMA5"] - df["SMA25"]
 
# diffの各値を直前のデータで引く　2ならゴールデンクロス(GC), -2ならデッドクロス(DC)と判定する
cross = np.where(np.sign(diff) - np.sign(diff.shift(1)) == 2, "GC", np.where(np.sign(diff) - np.sign(diff.shift(1)) == -2, "DC", np.nan))

def find_cross(short, long):
    # 差分を計算する
    diff = short - long
    
    # diffの各値を直前のデータで引く　2ならゴールデンクロス(GC), -2ならデッドクロス(DC)と判定する
    cross = np.where(np.sign(diff) - np.sign(diff.shift(1)) == 2, "GC", np.where(np.sign(diff) - np.sign(diff.shift(1)) == -2, "DC", np.nan))
    
    return cross
df["cross"] = find_cross(df["SMA5"],df["SMA25"])

# ゴールデンクロス
fig.add_trace(go.Scatter(x=df[df["cross"]=="GC"]["Date"], y=df[df["cross"]=="GC"]["MACD"]-50, name="GC", mode="markers", marker_symbol="triangle-up", marker_size=7, marker_color="black"), row=3, col=1)

                  # デッドクロス
fig.add_trace(go.Scatter(x=df[df["cross"]=="DC"]["Date"], y=df[df["cross"]=="DC"]["MACD"]+50, name="DC", mode="markers", marker_symbol="triangle-down", marker_size=7, marker_color="black"), row=3, col=1)

# Layout
fig.update_layout(
    title={
        "text": "トヨタ自動車(7203)の日足チャート",
        "y":0.9,
        "x":0.5,
    }
)
 
# y軸名を定義
fig.update_yaxes(title_text="株価", row=1, col=1)
fig.update_yaxes(title_text="出来高", row=2, col=1)
fig.update_yaxes(title_text="MACD", row=3, col=1)
 
# 不要な日付を非表示にする
#fig.update_xaxes(
#    rangebreaks=[dict(values=d_breaks)]
#)
 
fig.update(layout_xaxis_rangeslider_visible=False)
st.plotly_chart(fig)