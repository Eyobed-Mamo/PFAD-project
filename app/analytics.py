"""
Pure pandas analytics functions, kept separate from the Streamlit UI so
they're independently testable and reusable.
"""
import pandas as pd

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("month").apply(
        lambda x: pd.Series({
            "income": x.loc[x["type"] == "Income", "amount"].sum(),
            "expenses": -x.loc[x["type"] == "Expense", "amount"].sum(),
        }),
        include_groups=False
    ).reset_index()
    g["net"] = g["income"] - g["expenses"]
    g["savings_rate"] = g.apply(
        lambda r: (r["net"] / r["income"] * 100) if r["income"] > 0 else 0, axis=1
    )
    return g.sort_values("month")

def top_categories(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    expenses = df[df["type"] == "Expense"].copy()
    expenses["spend"] = -expenses["amount"]
    out = expenses.groupby("category")["spend"].sum().sort_values(ascending=False).head(n)
    return out.reset_index()

def category_by_month(df: pd.DataFrame) -> pd.DataFrame:
    expenses = df[df["type"] == "Expense"].copy()
    expenses["spend"] = -expenses["amount"]
    pivot = expenses.pivot_table(
        index="month", columns="category", values="spend", aggfunc="sum", fill_value=0
    )
    return pivot.sort_index()

def month_over_month(df: pd.DataFrame) -> pd.DataFrame:
    summary = monthly_summary(df)
    summary["expenses_change_pct"] = summary["expenses"].pct_change() * 100
    summary["income_change_pct"] = summary["income"].pct_change() * 100
    return summary

def overall_stats(df: pd.DataFrame) -> dict:
    income = df.loc[df["type"] == "Income", "amount"].sum()
    expenses = -df.loc[df["type"] == "Expense", "amount"].sum()
    net = income - expenses
    savings_rate = (net / income * 100) if income > 0 else 0
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net": net,
        "savings_rate": savings_rate,
        "n_transactions": len(df),
        "date_range": (df["date"].min(), df["date"].max()) if len(df) else (None, None),
    }
