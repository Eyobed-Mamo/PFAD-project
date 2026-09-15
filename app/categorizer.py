"""
Wraps the trained TF-IDF + Logistic Regression model and handles the
messy parts of turning a raw uploaded CSV into clean, categorized rows.
"""
import pickle
import re
from pathlib import Path
import pandas as pd

MODEL_PATH = Path(__file__).parent.parent / "models" / "categorizer_model.pkl"

_model = None

def get_model():
    global _model
    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


# Common column name variants seen across different bank export formats.
COLUMN_ALIASES = {
    "date": ["date", "transaction date", "posted date", "posting date"],
    "description": ["description", "transaction description", "memo", "merchant", "name"],
    "amount": ["amount", "transaction amount", "value"],
    "type": ["type", "transaction type", "debit/credit"],
}

def _match_column(columns, aliases):
    lower_map = {c.lower().strip(): c for c in columns}
    for alias in aliases:
        if alias in lower_map:
            return lower_map[alias]
    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map whatever the uploaded CSV calls its columns onto our schema."""
    resolved = {}
    for target, aliases in COLUMN_ALIASES.items():
        col = _match_column(df.columns, aliases)
        if col:
            resolved[target] = col

    missing = [k for k in ["date", "description", "amount"] if k not in resolved]
    if missing:
        raise ValueError(
            f"Couldn't find columns for: {', '.join(missing)}. "
            f"Your file needs a date, a description, and an amount column."
        )

    out = pd.DataFrame({
        "date": pd.to_datetime(df[resolved["date"]], errors="coerce"),
        "description": df[resolved["description"]].astype(str).str.strip(),
        "amount": pd.to_numeric(df[resolved["amount"]], errors="coerce"),
    })

    if "type" in resolved:
        raw_type = df[resolved["type"]].astype(str).str.lower()
        out["type"] = raw_type.apply(
            lambda v: "Income" if v in ("credit", "income", "deposit") else "Expense"
        )
    else:
        # Infer from sign of amount if no explicit type column exists.
        out["type"] = out["amount"].apply(lambda a: "Income" if a > 0 else "Expense")

    # Normalize sign: expenses negative, income positive, for consistent math later.
    out["amount"] = out.apply(
        lambda r: -abs(r["amount"]) if r["type"] == "Expense" else abs(r["amount"]),
        axis=1
    )

    before = len(out)
    out = out.dropna(subset=["date", "description", "amount"])
    dropped = before - len(out)

    out["month"] = out["date"].dt.strftime("%Y-%m")
    return out, dropped

def categorize(df: pd.DataFrame) -> pd.DataFrame:
    """Adds category + category_source columns using the trained model."""
    model = get_model()
    df = df.copy()
    cleaned = df["description"].str.lower()
    df["category"] = model.predict(cleaned)
    df["category_source"] = "model"

    # Anything the model is very unsure about, flag rather than silently guess.
    proba = model.predict_proba(cleaned)
    max_proba = proba.max(axis=1)
    low_confidence = max_proba < 0.35
    df.loc[low_confidence, "category"] = "Uncategorized"
    df.loc[low_confidence, "category_source"] = "low_confidence"

    return df
