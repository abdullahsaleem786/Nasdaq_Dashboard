
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

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Preprocessing
    df['Round Lot Size'] = pd.to_numeric(df['Round Lot Size'], errors='coerce')
    df.dropna(subset=['Round Lot Size'], inplace=True)

    # Filters
    exchanges = st.multiselect("Select Listing Exchange(s):", options=df['Listing Exchange'].unique(), default=df['Listing Exchange'].unique())
    etf_filter = st.selectbox("Filter by ETF status:", options=['All', 'Y', 'N'])
    status_filter = st.selectbox("Filter by Financial Status:", options=['All'] + list(df['Financial Status'].dropna().unique()))

    # Apply filters
    if exchanges:
        df = df[df['Listing Exchange'].isin(exchanges)]
    if etf_filter != 'All':
        df = df[df['ETF'] == etf_filter]
    if status_filter != 'All':
        df = df[df['Financial Status'] == status_filter]

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ETF vs Non-ETF Count (Interactive)")
        etf_fig = px.histogram(df, x='ETF', color='ETF', title="ETF Count", text_auto=True)
        st.plotly_chart(etf_fig, use_container_width=True)

    with col2:
        st.subheader("Stocks by Exchange")
        exchange_fig = px.histogram(df, x='Listing Exchange', color='Listing Exchange', title="Stocks by Exchange", text_auto=True)
        st.plotly_chart(exchange_fig, use_container_width=True)

    st.subheader("Boxplot: Round Lot Size by Exchange")
    box_fig = px.box(df, x='Listing Exchange', y='Round Lot Size', color='Listing Exchange')
    st.plotly_chart(box_fig, use_container_width=True)

    st.subheader("Violinplot: Round Lot Size by Financial Status")
    violin_fig = px.violin(df, x='Financial Status', y='Round Lot Size', color='Financial Status', box=True, points='all')
    st.plotly_chart(violin_fig, use_container_width=True)

    # Simulated trend data
    st.subheader("Simulated Stock Price Trend (Lineplot)")
    dates = pd.date_range(start='2024-01-01', periods=30)
    prices = np.random.randint(100, 200, size=30)
    df_trend = pd.DataFrame({'Date': dates, 'Price': prices})
    trend_fig = px.line(df_trend, x='Date', y='Price', markers=True)
    st.plotly_chart(trend_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📧 Email Report")
    with st.form("email_form"):
        sender_email = st.text_input("Your Gmail (sender)", value="mabdullahsaleem810@gmail.com")
        sender_password = st.text_input("Gmail Password / App Password", type="password")
        receiver_email = st.text_input("Send Report To (receiver)")
        subject = st.text_input("Email Subject", value="NASDAQ Dashboard Report")
        submit_btn = st.form_submit_button("Send Email with Report")

    if submit_btn:
        try:
            # Save chart image
            buffer = BytesIO()
            fig, ax = plt.subplots()
            df.groupby('Listing Exchange')['Round Lot Size'].mean().plot(kind='bar', ax=ax)
            plt.title("Avg Round Lot Size by Exchange")
            plt.xlabel("Exchange")
            plt.ylabel("Round Lot Size")
            plt.tight_layout()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Send email
            yag = yagmail.SMTP(sender_email, sender_password)
            yag.send(to=receiver_email, subject=subject,
                     contents=["Hi, here is your dashboard chart summary attached.", buffer])
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
else:
    st.info("👆 Please upload a CSV file to begin.")
