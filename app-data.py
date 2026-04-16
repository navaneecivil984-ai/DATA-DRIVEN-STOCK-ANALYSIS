import pandas as pd
import os
import streamlit as st

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Volatility Analysis", layout="wide")
st.title("⚡ Stock Volatility Analysis")

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
        
        # Convert columns
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        
        # Convert date (important)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Add ticker column
        ticker = file.replace(".csv", "")
        df['ticker'] = ticker
        
        all_data.append(df)

# ----------------------------------
# COMBINE DATA
# ----------------------------------
df = pd.concat(all_data, ignore_index=True)

# ----------------------------------
# SORT DATA (IMPORTANT)
# ----------------------------------
df = df.sort_values(by=['ticker', 'date'])

# ----------------------------------
# DAILY RETURNS
# ----------------------------------
df['daily_return'] = df.groupby('ticker')['close'].pct_change()

# Remove null values
df = df.dropna(subset=['daily_return'])

# ----------------------------------
# VOLATILITY (STD DEV)
# ----------------------------------
volatility_df = df.groupby('ticker')['daily_return'].std().reset_index()
volatility_df.rename(columns={'daily_return': 'volatility'}, inplace=True)

# ----------------------------------
# TOP 10 MOST VOLATILE
# ----------------------------------
top_volatile = volatility_df.sort_values(by='volatility', ascending=False).head(10)

# ----------------------------------
# DISPLAY
# ----------------------------------
st.subheader("📊 Top 10 Most Volatile Stocks")
st.dataframe(top_volatile)

st.subheader("📈 Volatility Bar Chart")
st.bar_chart(top_volatile.set_index('ticker')['volatility'])