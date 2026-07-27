import streamlit as st
import plotly.express as px

from utils import load_data, calculate_summary, monthly_summary

st.set_page_config(
    page_title="FinanceDash AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 FinanceDash AI")
st.caption("Interactive Personal Finance Dashboard")

uploaded_file = st.file_uploader(
    "Upload your finance CSV file",
    type=["csv"]
)

if uploaded_file:

    df = load_data(uploaded_file)

    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)

    summary = calculate_summary(df)

    col1, col2, col3 = st.columns(3)

    col1.metric("Income", f"₹{summary['Income']:,.2f}")
    col2.metric("Expense", f"₹{summary['Expense']:,.2f}")
    col3.metric("Savings", f"₹{summary['Savings']:,.2f}")

    st.divider()

    st.subheader("Income vs Expense")

    pie = px.pie(
        names=["Income", "Expense"],
        values=[
            summary["Income"],
            summary["Expense"]
        ]
    )

    st.plotly_chart(pie, use_container_width=True)

    st.subheader("Monthly Trends")

    monthly = monthly_summary(df)

    bar = px.bar(
        monthly,
        x="Month",
        y=["Income", "Expense"],
        barmode="group"
    )

    st.plotly_chart(bar, use_container_width=True)

    st.subheader("Download Processed Data")

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="finance_dashboard.csv",
        mime="text/csv"
    )

else:
    st.info("Upload a CSV file to begin.")
