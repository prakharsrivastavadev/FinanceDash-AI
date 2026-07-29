import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Date",
    "Type",
    "Amount",
]


def load_data(uploaded_file):
    """
    Safely load and validate finance data.
    """

    if uploaded_file is None:
        raise ValueError("No CSV file uploaded.")

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Unable to read CSV: {e}")

    if df.empty:
        raise ValueError("Uploaded CSV is empty.")

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    df = df.copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce",
    )

    df["Type"] = (
        df["Type"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.title()
    )

    df = df.dropna(
        subset=[
            "Date",
            "Amount",
        ]
    )

    valid_types = {
        "Income",
        "Expense",
    }

    df.loc[
        ~df["Type"].isin(valid_types),
        "Type",
    ] = "Unknown"

    df = df.reset_index(drop=True)

    return df


def calculate_summary(df):
    """
    Safely calculate financial summary.
    """

    if df.empty:
        return {
            "Income": 0.0,
            "Expense": 0.0,
            "Savings": 0.0,
        }

    income = float(
        df.loc[
            df["Type"] == "Income",
            "Amount",
        ].sum()
    )

    expense = float(
        df.loc[
            df["Type"] == "Expense",
            "Amount",
        ].sum()
    )

    savings = income - expense

    return {
        "Income": income,
        "Expense": expense,
        "Savings": savings,
    }


def monthly_summary(df):
    """
    Monthly income and expense totals.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Month",
                "Income",
                "Expense",
            ]
        )

    temp = df.copy()

    temp["Month"] = (
        temp["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    summary = (
        temp.groupby(
            ["Month", "Type"]
        )["Amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    for column in ["Income", "Expense"]:
        if column not in summary.columns:
            summary[column] = 0.0

    return summary
