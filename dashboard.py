import streamlit as st
import sqlite3
import pandas as pd

# Set up the web page layout
st.set_page_config(page_title="Agency AI Dashboard", layout="wide")
st.title("📊 AI Customer Support Dashboard")

# Connect to the SQLite database
conn = sqlite3.connect('email_analytics.db')
df = pd.read_sql_query("SELECT * FROM email_logs", conn)

if df.empty:
    st.warning("No data found! Please run your ai_brain.py script first to generate logs.")
else:
    # --- Top Level Metrics ---
    st.subheader("Performance Metrics")
    col1, col2, col3 = st.columns(3)
    
    total_emails = len(df)
    pass_rate = (len(df[df['qa_status'] == 'PASS']) / total_emails) * 100 if total_emails > 0 else 0
    avg_time = df['processing_time'].mean()
    
    col1.metric("Total Emails Processed", total_emails)
    col2.metric("QA Pass Rate", f"{pass_rate:.1f}%")
    col3.metric("Avg Processing Time", f"{avg_time:.2f}s")
    
    st.divider()

    # --- Charts ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Emails by Category")
        category_counts = df['category'].value_counts()
        st.bar_chart(category_counts)
        
    with col_chart2:
        st.subheader("Quality Assurance Status")
        qa_counts = df['qa_status'].value_counts()
        st.bar_chart(qa_counts)
        
    st.divider()
    
    # --- Raw Data Table ---
    st.subheader("Raw Email Logs")
    st.dataframe(df, use_container_width=True)