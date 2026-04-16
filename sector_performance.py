import streamlit as st
import pandas as pd

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Sector Performance", layout="wide")
st.title("📊 Sector-wise Stock Performance")

# ----------------------------------
# FILE PATHS
# ----------------------------------
stock_path = r"C:\Users\ADMIN\Documents\PAGES\DATA PROCESS\combined_data.csv"
sector_path = r"C:\Users\ADMIN\Documents\PAGES\DATA PROCESS\sector_data.csv"

try:
    # ----------------------------------
    # LOAD DATA
    # ----------------------------------
    stock_df = pd.read_csv(stock_path)
    sector_df = pd.read_csv(sector_path)

    # Clean columns
    stock_df.columns = stock_df.columns.str.strip().str.lower()
    sector_df.columns = sector_df.columns.str.strip().str.lower()

    # ----------------------------------
    # MERGE (CLASSIFY STOCKS BY SECTOR)
    # ----------------------------------
    df = pd.merge(stock_df, sector_df[['ticker', 'sector']], on='ticker', how='left')
    df['sector'] = df['sector'].fillna("Unknown")

    # ----------------------------------
    # PREPARE DATA
    # ----------------------------------
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df = df.sort_values(['ticker', 'date'])

    # ----------------------------------
    # YEARLY RETURN (PER STOCK)
    # ----------------------------------
    yearly = df.groupby(['ticker', 'year']).agg(
        start_price=('close', 'first'),
        end_price=('close', 'last')
    ).reset_index()

    yearly['return'] = (
        (yearly['end_price'] - yearly['start_price']) /
        yearly['start_price']
    )

    # Add sector
    yearly = pd.merge(
        yearly,
        df[['ticker', 'sector']].drop_duplicates(),
        on='ticker',
        how='left'
    )

    # ----------------------------------
    # SIDEBAR FILTER
    # ----------------------------------
    st.sidebar.header("🔍 Filter")

    years = sorted(yearly['year'].unique())
    selected_year = st.sidebar.selectbox("📅 Select Year", years)

    filtered = yearly[yearly['year'] == selected_year]

    # ----------------------------------
    # SECTOR PERFORMANCE (MAIN LOGIC)
    # ----------------------------------
    sector_perf = filtered.groupby('sector')['return'].mean().reset_index()
    sector_perf['return'] *= 100
    sector_perf = sector_perf.sort_values(by='return', ascending=False)

    # ----------------------------------
    # DISPLAY
    # ----------------------------------
    st.subheader(f"📊 Average Yearly Return by Sector ({selected_year})")
    st.dataframe(sector_perf)

    # ----------------------------------
    # BAR CHART (REQUIRED VISUAL)
    # ----------------------------------
    st.subheader("📈 Sector Performance")
    st.bar_chart(sector_perf.set_index('sector'))

    # ----------------------------------
    # INSIGHTS
    # ----------------------------------
    if not sector_perf.empty:
        best = sector_perf.iloc[0]
        worst = sector_perf.iloc[-1]

        st.markdown("### 📌 Key Insights")
        st.success(f"🏆 Best Sector: {best['sector']} ({best['return']:.2f}%)")
        st.error(f"📉 Worst Sector: {worst['sector']} ({worst['return']:.2f}%)")

except Exception as e:
    st.error(f"⚠️ Error: {e}")