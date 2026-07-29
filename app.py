import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    calculate_summary,
    monthly_summary,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="FinanceDash AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.main{
    padding-top:1rem;
}

.stMetric{
    border-radius:10px;
    padding:10px;
}

footer{
    visibility:hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📈 FinanceDash AI")

st.caption(
    "AI-powered Personal Finance Dashboard"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Upload Financial Dataset")

st.sidebar.info(
"""
Required CSV columns:

• Date
• Type
• Amount
"""
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
)

# --------------------------------------------------
# Wait for Upload
# --------------------------------------------------

if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin."
    )

    st.stop()

# --------------------------------------------------
# Safe Data Loading
# --------------------------------------------------

try:

    df = load_data(uploaded_file)

except Exception as e:

    st.error(
        "Unable to load dataset."
    )

    st.exception(e)

    st.stop()

# --------------------------------------------------
# Empty Dataset Check
# --------------------------------------------------

if df.empty:

    st.warning(
        "Dataset contains no valid records."
    )

    st.stop()
    # --------------------------------------------------
# Financial Summary
# --------------------------------------------------

try:

    summary = calculate_summary(df)

except Exception as e:

    st.error(
        "Unable to calculate financial summary."
    )

    st.exception(e)

    st.stop()

st.subheader("📊 Financial Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "💰 Total Income",
        f"₹{summary['Income']:,.2f}",
    )

with col2:

    st.metric(
        "💸 Total Expenses",
        f"₹{summary['Expense']:,.2f}",
    )

with col3:

    st.metric(
        "🏦 Net Savings",
        f"₹{summary['Savings']:,.2f}",
    )

st.divider()

# --------------------------------------------------
# Dataset Statistics
# --------------------------------------------------

st.subheader("📈 Dataset Statistics")

left, right = st.columns(2)

with left:

    st.write(
        f"**Transactions:** {len(df)}"
    )

    st.write(
        f"**Date Range:** "
        f"{df['Date'].min().date()} → "
        f"{df['Date'].max().date()}"
    )

with right:

    st.write(
        f"**Income Records:** "
        f"{(df['Type'] == 'Income').sum()}"
    )

    st.write(
        f"**Expense Records:** "
        f"{(df['Type'] == 'Expense').sum()}"
    )

st.divider()

# --------------------------------------------------
# Recent Transactions
# --------------------------------------------------

st.subheader("📋 Recent Transactions")

recent_df = (
    df.sort_values(
        by="Date",
        ascending=False,
    )
    .reset_index(drop=True)
)

st.dataframe(
    recent_df.head(15),
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Transaction Filter
# --------------------------------------------------

st.subheader("🔍 Transaction Explorer")

transaction_type = st.selectbox(
    "Transaction Type",
    [
        "All",
        "Income",
        "Expense",
    ],
)

if transaction_type == "All":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["Type"] == transaction_type
    ].copy()

filtered_df = filtered_df.reset_index(
    drop=True
)

# --------------------------------------------------
# Date Filter
# --------------------------------------------------

min_date = filtered_df["Date"].min().date()

max_date = filtered_df["Date"].max().date()

selected_dates = st.date_input(
    "Date Range",
    value=(
        min_date,
        max_date,
    ),
    min_value=min_date,
    max_value=max_date,
)

try:

    if (
        isinstance(selected_dates, tuple)
        and
        len(selected_dates) == 2
    ):

        start_date, end_date = selected_dates

        filtered_df = filtered_df[
            (
                filtered_df["Date"].dt.date
                >= start_date
            )
            &
            (
                filtered_df["Date"].dt.date
                <= end_date
            )
        ]

except Exception:

    pass

filtered_df = filtered_df.reset_index(
    drop=True
)

# --------------------------------------------------
# Transaction Table
# --------------------------------------------------

st.write(
    f"Showing **{len(filtered_df):,}** transaction(s)."
)

if filtered_df.empty:

    st.warning(
        "No transactions found."
    )

else:

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# CSV Download
# --------------------------------------------------

try:

    csv = filtered_df.to_csv(
        index=False,
    ).encode("utf-8")

    st.download_button(
        "📥 Download Filtered CSV",
        csv,
        "filtered_finance.csv",
        "text/csv",
    )

except Exception as e:

    st.error(
        "Unable to prepare CSV download."
    )

    st.exception(e)

st.divider()

# --------------------------------------------------
# Transaction Statistics
# --------------------------------------------------

st.subheader("📌 Filter Statistics")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Transactions",
        len(filtered_df),
    )

with col2:

    st.metric(
        "Income",
        f"₹{filtered_df.loc[filtered_df['Type']=='Income','Amount'].sum():,.2f}"
    )

with col3:

    st.metric(
        "Expenses",
        f"₹{filtered_df.loc[filtered_df['Type']=='Expense','Amount'].sum():,.2f}"
    )

st.divider()
# --------------------------------------------------
# Financial Analytics
# --------------------------------------------------

st.subheader("📊 Financial Analytics")

# --------------------------------------------------
# Monthly Income vs Expense
# --------------------------------------------------

try:

    monthly_df = monthly_summary(df)

    if not monthly_df.empty:

        fig = px.bar(
            monthly_df,
            x="Month",
            y=["Income", "Expense"],
            barmode="group",
            title="Monthly Income vs Expense",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate monthly comparison."
    )

    st.exception(e)

# --------------------------------------------------
# Transaction Distribution
# --------------------------------------------------

try:

    type_summary = (
        filtered_df.groupby(
            "Type",
            as_index=False,
        )["Amount"]
        .sum()
    )

    if not type_summary.empty:

        fig = px.pie(
            type_summary,
            names="Type",
            values="Amount",
            hole=0.45,
            title="Income vs Expense Distribution",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate transaction distribution."
    )

    st.exception(e)

# --------------------------------------------------
# Daily Cash Flow
# --------------------------------------------------

try:

    daily_df = (
        filtered_df
        .groupby(
            filtered_df["Date"].dt.date,
            as_index=False,
        )["Amount"]
        .sum()
    )

    daily_df.columns = [
        "Date",
        "Amount",
    ]

    if not daily_df.empty:

        fig = px.line(
            daily_df,
            x="Date",
            y="Amount",
            markers=True,
            title="Daily Cash Flow",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate daily cash flow."
    )

    st.exception(e)

# --------------------------------------------------
# Transaction Amount Distribution
# --------------------------------------------------

try:

    fig = px.histogram(
        filtered_df,
        x="Amount",
        nbins=20,
        title="Transaction Amount Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate histogram."
    )

    st.exception(e)

# --------------------------------------------------
# Monthly Savings Trend
# --------------------------------------------------

try:

    savings_df = monthly_df.copy()

    savings_df["Savings"] = (
        savings_df["Income"]
        - savings_df["Expense"]
    )

    fig = px.line(
        savings_df,
        x="Month",
        y="Savings",
        markers=True,
        title="Monthly Savings Trend",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate savings trend."
    )

    st.exception(e)

st.divider()
# --------------------------------------------------
# Transaction Insights
# --------------------------------------------------

st.subheader("🧾 Transaction Insights")

display_df = filtered_df.reset_index(drop=True)

if display_df.empty:

    st.info(
        "No transactions available."
    )

else:

    selected_index = st.selectbox(
        "Select Transaction",
        options=range(len(display_df)),
        format_func=lambda x:
            f"{display_df.iloc[x]['Date'].date()} | "
            f"{display_df.iloc[x]['Type']} | "
            f"₹{display_df.iloc[x]['Amount']:,.2f}",
    )

    transaction = display_df.iloc[selected_index]

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Transaction Details")

        st.write(
            f"**Date:** {transaction['Date'].date()}"
        )

        st.write(
            f"**Type:** {transaction['Type']}"
        )

        st.write(
            f"**Amount:** ₹{transaction['Amount']:,.2f}"
        )

    with col2:

        st.write("### Financial Assessment")

        average_amount = display_df["Amount"].mean()

        if transaction["Amount"] >= average_amount * 2:

            st.error(
                "This transaction is significantly higher than the average transaction amount."
            )

        elif transaction["Amount"] >= average_amount:

            st.warning(
                "This transaction is above the average transaction amount."
            )

        else:

            st.success(
                "This transaction is below the average transaction amount."
            )

        transaction_count = int(
            (
                display_df["Type"]
                == transaction["Type"]
            ).sum()
        )

        st.write(
            f"**Transactions of this type:** {transaction_count}"
        )

st.divider()

# --------------------------------------------------
# Financial Breakdown
# --------------------------------------------------

st.subheader("📋 Financial Breakdown")

breakdown_df = (
    display_df
    .groupby(
        "Type",
        as_index=False,
    )["Amount"]
    .agg(
        Total="sum",
        Average="mean",
        Maximum="max",
        Minimum="min",
        Count="count",
    )
)

st.dataframe(
    breakdown_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Dataset Health Report
# --------------------------------------------------

st.subheader("🩺 Dataset Health Report")

total_records = len(df)

missing_values = int(df.isna().sum().sum())

duplicate_rows = int(df.duplicated().sum())

invalid_amounts = int((df["Amount"] < 0).sum())

invalid_dates = int(df["Date"].isna().sum())

health_score = max(
    0,
    100 - (
        missing_values
        + duplicate_rows
        + invalid_amounts
        + invalid_dates
    ),
)

health_score = min(100, health_score)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Records",
        total_records,
    )

    st.metric(
        "Missing Values",
        missing_values,
    )

with col2:

    st.metric(
        "Duplicate Rows",
        duplicate_rows,
    )

    st.metric(
        "Invalid Amounts",
        invalid_amounts,
    )

with col3:

    st.metric(
        "Invalid Dates",
        invalid_dates,
    )

    st.metric(
        "Dataset Quality",
        f"{health_score}%",
    )

st.divider()

# --------------------------------------------------
# Dataset Summary
# --------------------------------------------------

st.subheader("📋 Dataset Summary")

summary_df = pd.DataFrame(
    {
        "Metric": [
            "Rows",
            "Columns",
            "Income Transactions",
            "Expense Transactions",
            "Total Income",
            "Total Expense",
            "Net Savings",
        ],
        "Value": [
            len(df),
            len(df.columns),
            int((df["Type"] == "Income").sum()),
            int((df["Type"] == "Expense").sum()),
            f"₹{summary['Income']:,.2f}",
            f"₹{summary['Expense']:,.2f}",
            f"₹{summary['Savings']:,.2f}",
        ],
    }
)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "FinanceDash AI • Built with Streamlit, Pandas and Plotly"
)
















