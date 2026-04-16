import pandas as pd
import os
import streamlit as st

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Stock Market Analysis")

# ----------------------------------
# FOLDER PATH
# ----------------------------------
folder_path = r"C:\Users\ADMIN\Documents\PAGES\ALL_CSV_FILES"

all_data = []

# ----------------------------------
# READ + CLEAN + ADD TICKER
# ----------------------------------
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        
        df = pd.read_csv(file_path)
        
        df.columns = df.columns.str.lower().str.strip()
        
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        ticker = file.replace(".csv", "")
        df['ticker'] = ticker
        
        all_data.append(df)

# ----------------------------------
# COMBINE
# ----------------------------------
df = pd.concat(all_data, ignore_index=True)

# ----------------------------------
# GROUP BY STOCK
# ----------------------------------
df_grouped = df.groupby('ticker').agg({
    'open': 'first',
    'close': 'last',
    'volume': 'mean'
}).reset_index()

# ----------------------------------
# YEARLY RETURN
# ----------------------------------
df_grouped['yearly_return'] = ((df_grouped['close'] - df_grouped['open']) / df_grouped['open']) * 100

# ----------------------------------
# TOP & LOSS STOCKS
# ----------------------------------
top_10_green = df_grouped.sort_values(by='yearly_return', ascending=False).head(10)
top_10_loss = df_grouped.sort_values(by='yearly_return', ascending=True).head(10)

# ----------------------------------
# MARKET SUMMARY
# ----------------------------------
green_stocks = (df_grouped['yearly_return'] > 0).sum()
red_stocks = (df_grouped['yearly_return'] < 0).sum()
avg_price = df_grouped['close'].mean()
avg_volume = df_grouped['volume'].mean()

# ----------------------------------
# DISPLAY METRICS
# ----------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("🟢 Green Stocks", green_stocks)
col2.metric("🔴 Red Stocks", red_stocks)
col3.metric("💰 Avg Price", f"{avg_price:.2f}")
col4.metric("📦 Avg Volume", f"{avg_volume:.2f}")

st.divider()

# ----------------------------------
# TABLE DISPLAY
# ----------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Green Stocks")
    st.dataframe(top_10_green)

with col2:
    st.subheader("📉 Top 10 Loss Stocks")
    st.dataframe(top_10_loss)

# ----------------------------------
# CHART
# ----------------------------------
st.subheader("📊 Top 10 Green Stocks (Return %)")

st.bar_chart(top_10_green.set_index('ticker')['yearly_return'])