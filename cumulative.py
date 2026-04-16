import pandas as pd
import os
import streamlit as st

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Cumulative Return", layout="wide")
st.title("📈 Cumulative Return Over Time")

# ----------------------------------
# FOLDER PATH
# ----------------------------------
folder_path = r"C:\Users\ADMIN\Documents\PAGES\ALL_CSV_FILES"

all_data = []

# ----------------------------------
# READ ALL CSV FILES
# ----------------------------------
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Convert types
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Add ticker
        ticker = file.replace(".csv", "")
        df['ticker'] = ticker
        
        all_data.append(df)

# ----------------------------------
# COMBINE DATA
# ----------------------------------
df = pd.concat(all_data, ignore_index=True)

# ----------------------------------
# SORT DATA
# ----------------------------------
df = df.sort_values(by=['ticker', 'date'])

# ----------------------------------
# DAILY RETURNS
# ----------------------------------
df['daily_return'] = df.groupby('ticker')['close'].pct_change()

# Remove nulls
df = df.dropna(subset=['daily_return'])

# ----------------------------------
# CUMULATIVE RETURN
# ----------------------------------
df['cumulative_return'] = (1 + df['daily_return']).groupby(df['ticker']).cumprod()

# ----------------------------------
# FIND TOP 5 PERFORMING STOCKS
# ----------------------------------
final_returns = df.groupby('ticker')['cumulative_return'].last().reset_index()

top_5 = final_returns.sort_values(by='cumulative_return', ascending=False).head(5)

top_5_tickers = top_5['ticker'].tolist()

# ----------------------------------
# FILTER DATA FOR TOP 5
# ----------------------------------
top_df = df[df['ticker'].isin(top_5_tickers)]

# ----------------------------------
# DISPLAY
# ----------------------------------
st.subheader("🏆 Top 5 Performing Stocks (Cumulative Return)")
st.dataframe(top_5)

st.subheader("📊 Cumulative Return Line Chart")

# Pivot for line chart
pivot_df = top_df.pivot(index='date', columns='ticker', values='cumulative_return')

st.line_chart(pivot_df)