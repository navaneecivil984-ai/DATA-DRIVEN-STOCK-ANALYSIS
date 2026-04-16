import streamlit as st
import pandas as pd
import os

# ----------------------------------
# 1. GLOBAL CONFIG & STYLING
# ----------------------------------
st.set_page_config(page_title="Ultimate Stock Analytics Hub", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------
# 2. SHARED DATA LOADING FUNCTIONS
# ----------------------------------
@st.cache_data
def load_all_csv_data(folder_path):
    all_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower().str.strip()
            # Convert types
            for col in ['open', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            df['ticker'] = file.replace(".csv", "")
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

@st.cache_data
def load_combined_csv(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'])
    return df

# Paths (Adjusted to your local paths)
FOLDER_PATH = r"C:\Users\ADMIN\Documents\PAGES\ALL_CSV_FILES"
COMBINED_PATH = r"C:\Users\ADMIN\Documents\PAGES\DATA PROCESS\combined_data.csv"
SECTOR_PATH = r"C:\Users\ADMIN\Documents\PAGES\DATA PROCESS\sector_data.csv"

# ----------------------------------
# 3. SIDEBAR NAVIGATION
# ----------------------------------
st.sidebar.title("🚀 Navigation")
page = st.sidebar.radio("Go to:", [
    "📈 Stock Market Analysis",
    "⚡ Volatility Analysis",
    "📊 Cumulative Returns",
    "🏢 Sector Performance",
    "🔗 Correlation Matrix",
    "📅 Monthly Gainers/Losers"
])

# ----------------------------------
# PAGE 1: STOCK MARKET ANALYSIS
# ----------------------------------
if page == "📈 Stock Market Analysis":
    st.title("📊 General Stock Market Analysis")
    df = load_all_csv_data(FOLDER_PATH)
    
    df_grouped = df.groupby('ticker').agg({
        'open': 'first', 'close': 'last', 'volume': 'mean'
    }).reset_index()
    
    df_grouped['yearly_return'] = ((df_grouped['close'] - df_grouped['open']) / df_grouped['open']) * 100
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🟢 Green Stocks", (df_grouped['yearly_return'] > 0).sum())
    m2.metric("🔴 Red Stocks", (df_grouped['yearly_return'] < 0).sum())
    m3.metric("💰 Avg Price", f"{df_grouped['close'].mean():.2f}")
    m4.metric("📦 Avg Volume", f"{df_grouped['volume'].mean():.0f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top 10 Green stocks")
        st.dataframe(df_grouped.sort_values('yearly_return', ascending=False).head(10), use_container_width=True)
    with col2:
        st.subheader("📉 Top 10 Red stocks")
        st.dataframe(df_grouped.sort_values('yearly_return', ascending=True).head(10), use_container_width=True)

    st.subheader("Visualizing Performance (%)")
    st.bar_chart(df_grouped.sort_values('yearly_return', ascending=False).head(10).set_index('ticker')['yearly_return'])

# ----------------------------------
# PAGE 2: VOLATILITY
# ----------------------------------
elif page == "⚡ Volatility Analysis":
    st.title("⚡ Stock Volatility Analysis")
    df = load_all_csv_data(FOLDER_PATH).sort_values(['ticker', 'date'])
    df['daily_return'] = df.groupby('ticker')['close'].pct_change()
    
    vol_df = df.dropna(subset=['daily_return']).groupby('ticker')['daily_return'].std().reset_index()
    vol_df.rename(columns={'daily_return': 'volatility'}, inplace=True)
    top_vol = vol_df.sort_values('volatility', ascending=False).head(10)
    
    st.dataframe(top_vol, use_container_width=True)
    st.subheader("Top 10 Most Volatile Stocks")
    st.bar_chart(top_vol.set_index('ticker')['volatility'])

# ----------------------------------
# PAGE 3: CUMULATIVE RETURNS
# ----------------------------------
elif page == "📊 Cumulative Returns":
    st.title("📈 Cumulative Return Over Time")
    df = load_all_csv_data(FOLDER_PATH).sort_values(['ticker', 'date'])
    df['daily_return'] = df.groupby('ticker')['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).groupby(df['ticker']).cumprod()
    
    final_ret = df.groupby('ticker')['cumulative_return'].last().nlargest(5).index.tolist()
    pivot_df = df[df['ticker'].isin(final_ret)].pivot(index='date', columns='ticker', values='cumulative_return')
    
    st.subheader("Growth of $1 Investment (Top 5 Stocks)")
    st.line_chart(pivot_df)
    st.dataframe(pivot_df.tail(1).T.rename(columns={pivot_df.index[-1]: "Final Multiple"}))

# ----------------------------------
# PAGE 4: SECTOR PERFORMANCE
# ----------------------------------
elif page == "🏢 Sector Performance":
    st.title("🏢 Sector-wise Performance")
    try:
        stock_df = load_combined_csv(COMBINED_PATH)
        sector_df = pd.read_csv(SECTOR_PATH)
        sector_df.columns = sector_df.columns.str.strip().str.lower()
        
        df = pd.merge(stock_df, sector_df[['ticker', 'sector']], on='ticker', how='left').fillna("Unknown")
        df['year'] = df['date'].dt.year
        
        selected_year = st.sidebar.selectbox("Select Year", sorted(df['year'].unique(), reverse=True))
        
        yearly = df[df['year'] == selected_year].groupby(['ticker', 'sector']).agg(
            start=('close', 'first'), end=('close', 'last')
        ).reset_index()
        yearly['return'] = ((yearly['end'] - yearly['start']) / yearly['start']) * 100
        
        sector_perf = yearly.groupby('sector')['return'].mean().sort_values(ascending=False).reset_index()
        
        st.subheader(f"Average Sector Returns in {selected_year}")
        st.bar_chart(sector_perf.set_index('sector'))
        st.table(sector_perf)
    except Exception as e:
        st.error(f"Missing sector file: {e}")

# ----------------------------------
# PAGE 5: CORRELATION
# ----------------------------------
elif page == "🔗 Correlation Matrix":
    st.title("🔗 Stock Correlation Matrix")
    df = load_combined_csv(COMBINED_PATH)
    pivot_df = df.pivot(index='date', columns='ticker', values='close').pct_change().dropna()
    
    selected_stocks = st.multiselect("Select Stocks to Compare", pivot_df.columns.tolist(), default=pivot_df.columns.tolist()[:8])
    
    if selected_stocks:
        corr_matrix = pivot_df[selected_stocks].corr()
        st.subheader("Price Movement Correlation (Returns)")
        st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format(precision=2))
    else:
        st.warning("Please select at least two stocks.")

# ----------------------------------
# PAGE 6: MONTHLY GAINERS
# ----------------------------------
elif page == "📅 Monthly Gainers/Losers":
    st.title("📅 Monthly Market Leaders")
    df = load_combined_csv(COMBINED_PATH)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    
    # Sort logically
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    monthly = df.groupby(['ticker', 'year', 'month']).agg(start=('close', 'first'), end=('close', 'last')).reset_index()
    monthly['return'] = ((monthly['end'] - monthly['start']) / monthly['start']) * 100
    
    # Filter selection
    sel_year = st.sidebar.selectbox("Year", sorted(monthly['year'].unique(), reverse=True))
    sel_month = st.sidebar.selectbox("Month", month_order)
    
    data = monthly[(monthly['year'] == sel_year) & (monthly['month'] == sel_month)]
    
    if not data.empty:
        col1, col2 = st.columns(2)
        col1.subheader("🚀 Top 5 Gainers")
        col1.table(data.nlargest(5, 'return')[['ticker', 'return']])
        
        col2.subheader("📉 Top 5 Losers")
        col2.table(data.nsmallest(5, 'return')[['ticker', 'return']])
    else:
        st.info("No data available for the selected month/year.")