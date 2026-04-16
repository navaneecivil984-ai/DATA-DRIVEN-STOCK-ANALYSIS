import streamlit as st
import pandas as pd

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Monthly Gainers & Losers", layout="wide")
st.title("📊 Top 5 Gainers & Losers (Month-wise with Year)")

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
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df = df.sort_values(['ticker', 'date'])

    # ----------------------------------
    # MONTHLY RETURNS
    # ----------------------------------
    monthly = df.groupby(['ticker', 'year', 'month']).agg(
        start_price=('close', 'first'),
        end_price=('close', 'last')
    ).reset_index()

    monthly['return'] = (
        (monthly['end_price'] - monthly['start_price']) /
        monthly['start_price']
    ) * 100

    # ----------------------------------
    # MONTH NAMES
    # ----------------------------------
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    # ----------------------------------
    # DISPLAY YEAR + MONTH
    # ----------------------------------
    grouped = monthly.groupby(['year', 'month'])

    for (year, month), data in grouped:

        st.subheader(f"📅 {month_names[month]} {year}")

        # Top gainers
        gainers = data.sort_values(by='return', ascending=False).head(5)

        # Top losers
        losers = data.sort_values(by='return', ascending=True).head(5)

        # Combine
        result = pd.concat([gainers, losers])

        # Label
        result['type'] = result['return'].apply(
            lambda x: "Gainer" if x > 0 else "Loser"
        )

        # Display table
        st.dataframe(result[['ticker', 'return', 'type']])

except Exception as e:
    st.error(f"⚠️ Error: {e}")