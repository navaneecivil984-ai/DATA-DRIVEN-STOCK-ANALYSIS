import streamlit as st
import pandas as pd

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Stock Correlation", layout="wide")
st.title("📊 Stock Price Correlation (Heatmap Style Table)")

# ----------------------------------
# FILE PATH
# ----------------------------------
file_path = r"C:\Users\ADMIN\Documents\PAGES\DATA PROCESS\combined_data.csv"

try:
    # ----------------------------------
    # LOAD DATA
    # ----------------------------------
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()

    # ----------------------------------
    # PREPARE DATA
    # ----------------------------------
    df['date'] = pd.to_datetime(df['date'])

    # Pivot table
    pivot_df = df.pivot(index='date', columns='ticker', values='close')

    # ----------------------------------
    # RETURNS (IMPORTANT)
    # ----------------------------------
    returns = pivot_df.pct_change().dropna()

    # ----------------------------------
    # CORRELATION MATRIX
    # ----------------------------------
    corr_matrix = returns.corr()

    # ----------------------------------
    # SIDEBAR FILTER
    # ----------------------------------
    st.sidebar.header("🔍 Filter Stocks")

    tickers = corr_matrix.columns.tolist()

    selected_stocks = st.sidebar.multiselect(
        "Select Stocks",
        tickers,
        default=tickers[:10]
    )

    filtered_corr = corr_matrix.loc[selected_stocks, selected_stocks]

    # ----------------------------------
    # DISPLAY MATRIX
    # ----------------------------------
    st.subheader("📄 Correlation Matrix")
    st.dataframe(filtered_corr)

    # ----------------------------------
    # HEATMAP STYLE (COLOR GRADIENT)
    # ----------------------------------
    st.subheader("🔥 Heatmap View (Color Gradient)")

    styled = filtered_corr.style.background_gradient(cmap='coolwarm')

    st.dataframe(styled)

except Exception as e:
    st.error(f"⚠️ Error: {e}")