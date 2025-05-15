import streamlit as st
import pandas as pd
import yfinance as yf

st.title("Apirine Slow RSI 選股器 (台股+美股)")

symbols = [
    "AAPL", "MSFT", "NVDA", "TSLA", "META", "AMZN", "GOOG",
    "2330.TW", "2303.TW", "0050.TW", "2317.TW", "2412.TW", "2603.TW", "2882.TW"
]

smoothing = st.slider("Smoothing", 2, 20, 6)
rsi_len = st.slider("RSI Length", 2, 30, 14)

def wima(series, length):
    result = []
    prev = 0
    for val in series:
        next_val = (val + prev * (length - 1)) / length
        result.append(next_val)
        prev = next_val
    return pd.Series(result, index=series.index)

def calc_slow_rsi(df):
    ema_price = df['Close'].ewm(span=smoothing, adjust=False).mean()
    r2 = (df['Close'] - ema_price).clip(lower=0)
    r3 = (ema_price - df['Close']).clip(lower=0)
    r4 = wima(r2, rsi_len)
    r5 = wima(r3, rsi_len)
    slow_rsi = 100 - (100 / (1 + (r4 / r5)))
    return slow_rsi

results = []
for symbol in symbols:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30:
            continue
        df["SlowRSI"] = calc_slow_rsi(df)
        latest_rsi = df["SlowRSI"].iloc[-1]
        pre_rsi = df["SlowRSI"].iloc[-2]
        if pre_rsi < 30 and latest_rsi > 30 and latest_rsi > pre_rsi:
            results.append({
                "股票代碼": symbol,
                "Slow RSI": round(latest_rsi, 2),
                "收盤價": round(df["Close"].iloc[-1], 2),
                "成交量": int(df["Volume"].iloc[-1])
            })
    except:
        continue

st.subheader("符合條件股票：")
st.dataframe(pd.DataFrame(results))
