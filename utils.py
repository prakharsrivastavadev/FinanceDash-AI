import pandas as pd


def load_data(uploaded_file):
    """Load CSV file into a DataFrame."""
    return pd.read_csv(uploaded_file)


def calculate_summary(df):
    """Calculate key financial metrics."""

    income = df[df["Type"] == "Income"]["Amount"].sum()
    expense = df[df["Type"] == "Expense"]["Amount"].sum()
    savings = income - expense

    return {
        "Income": income,
        "Expense": expense,
        "Savings": savings,
    }


def monthly_summary(df):
    """Return monthly income and expense totals."""

    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    summary = (
        df.groupby(["Month", "Type"])["Amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    return summary
