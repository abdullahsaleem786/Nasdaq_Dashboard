import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yagmail
from io import BytesIO
import matplotlib.pyplot as plt

# Streamlit page config
st.set_page_config(page_title="NASDAQ Dashboard", layout="wide")
st.title("📊 NASDAQ Metadata Dashboard with Email Report")

# Load sample data automatically
@st.cache_data
def load_sample_data():
    return pd.DataFrame({
        'Symbol': ['AAPL', 'TSLA', 'MSFT', 'AMZN', 'META', 'QQQ', 'SPY', 'IWM', 'GLD', 'TLT'],
        'Listing Exchange': ['NASDAQ', 'NASDAQ', 'NASDAQ', 'NASDAQ', 'NASDAQ', 'NYSE', 'NYSE', 'NYSE', 'NYSE', 'NYSE'],
        'Round Lot Size': [100, 50, 100, 10, 100, 50, 100, 50, 10, 50],
        'ETF': ['N', 'N', 'N', 'N', 'N', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'Financial Status': ['Normal', 'Normal', 'Normal', 'Deficient', 'Normal', 
                           'Normal', 'Normal', 'Deficient', 'Normal', 'Normal'],
        'Market Cap': [2.5e12, 800e9, 2.0e12, 1.5e12, 700e9, 200e9, 400e9, 50e9, 60e9, 30e9]
    })

df = load_sample_data()
st.success("✅ Loaded sample NASDAQ market data. Explore the dashboard below!")

# Filters
st.sidebar.header("Filters")
exchanges = st.sidebar.multiselect(
    "Select Listing Exchange(s):",
    options=df['Listing Exchange'].unique(),
    default=df['Listing Exchange'].unique()
)

etf_filter = st.sidebar.selectbox(
    "Filter by ETF status:",
    options=['All', 'Y', 'N'],
    index=0
)

status_filter = st.sidebar.selectbox(
    "Filter by Financial Status:",
    options=['All'] + list(df['Financial Status'].dropna().unique()),
    index=0
)

# Apply filters
if exchanges:
    df = df[df['Listing Exchange'].isin(exchanges)]
if etf_filter != 'All':
    df = df[df['ETF'] == etf_filter]
if status_filter != 'All':
    df = df[df['Financial Status'] == status_filter]

# Dashboard Layout
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("ETF vs Non-ETF Count")
    etf_fig = px.histogram(df, x='ETF', color='ETF', 
                          title="ETF Count", text_auto=True)
    st.plotly_chart(etf_fig, use_container_width=True)

with col2:
    st.subheader("Stocks by Exchange")
    exchange_fig = px.histogram(df, x='Listing Exchange', 
                               color='Listing Exchange', 
                               title="Stocks by Exchange", 
                               text_auto=True)
    st.plotly_chart(exchange_fig, use_container_width=True)

st.subheader("Market Capitalization Distribution")
market_cap_fig = px.box(df, y='Market Cap', 
                       title="Market Cap (in billions)", 
                       log_y=True)
st.plotly_chart(market_cap_fig, use_container_width=True)

st.subheader("Round Lot Size Analysis")
tab1, tab2 = st.tabs(["By Exchange", "By Financial Status"])
with tab1:
    box_fig = px.box(df, x='Listing Exchange', y='Round Lot Size')
    st.plotly_chart(box_fig, use_container_width=True)
with tab2:
    violin_fig = px.violin(df, x='Financial Status', y='Round Lot Size', box=True)
    st.plotly_chart(violin_fig, use_container_width=True)

# Email Report Section
st.markdown("---")
st.subheader("📧 Generate Email Report")
with st.form("email_form"):
    sender_email = st.text_input("Your Gmail", value="your_email@gmail.com")
    sender_password = st.text_input("App Password", type="password")
    receiver_email = st.text_input("Recipient Email")
    subject = st.text_input("Subject", value="NASDAQ Dashboard Report")
    
    if st.form_submit_button("Send Report"):
        try:
            buffer = BytesIO()
            fig, ax = plt.subplots(figsize=(10, 6))
            df.groupby('Listing Exchange')['Market Cap'].mean().plot(
                kind='bar', ax=ax, color=['#1f77b4', '#ff7f0e'])
            plt.title("Average Market Cap by Exchange")
            plt.ylabel("Market Cap (Billions)")
            plt.tight_layout()
            fig.savefig(buffer, format='png')
            buffer.seek(0)
            
            yag = yagmail.SMTP(sender_email, sender_password)
            yag.send(
                to=receiver_email,
                subject=subject,
                contents=[
                    "Here's your NASDAQ dashboard report:",
                    buffer
                ]
            )
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {str(e)}")