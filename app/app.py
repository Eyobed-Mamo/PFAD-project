import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import uuid

import db
import categorizer
import analytics

st.set_page_config(page_title="Personal Finance Analytics Dashboard", layout="wide")

st.title("💰 Personal Finance Analytics Dashboard")
st.caption(
    "Upload a transaction CSV and get automatic categorization "
    "(via a trained ML classifier) plus a full spending analysis."
)

# ---------- Upload ----------
with st.sidebar:
    st.header("Upload")
    uploaded_file = st.file_uploader("Transaction CSV", type=["csv"])
    st.caption(
        "Needs a date, description, and amount column. "
        "A debit/credit or type column is optional -- we'll infer it "
        "from the amount sign if it's missing."
    )

    if uploaded_file is not None:
        try:
            raw = pd.read_csv(uploaded_file)
            normalized, dropped = categorizer.normalize_columns(raw)
            categorized = categorizer.categorize(normalized)

            batch_id = str(uuid.uuid4())[:8]
            db.insert_transactions(categorized, batch_id)

            st.success(f"Loaded {len(categorized)} transactions.")
            if dropped:
                st.warning(f"Skipped {dropped} rows with missing/unparseable date, description, or amount.")

            n_low_conf = (categorized["category_source"] == "low_confidence").sum()
            if n_low_conf:
                st.info(f"{n_low_conf} transaction(s) marked 'Uncategorized' -- the model wasn't confident enough to guess.")
        except ValueError as e:
            st.error(str(e))

    st.divider()
    batches = db.list_batches()
    if not batches.empty:
        st.caption(f"{len(batches)} upload batch(es) stored")
        if st.button("Clear all data", type="secondary"):
            db.clear_all()
            st.rerun()

# ---------- Load data ----------
df = db.load_all_transactions()

if df.empty:
    st.info("Upload a CSV to get started, or try the sample file in the repo (`sample_data/sample_transactions.csv`).")
    st.stop()

# ---------- Filters ----------
st.sidebar.header("Filters")
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))
categories_available = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect("Categories", categories_available, default=categories_available)
types_available = sorted(df["type"].unique())
selected_types = st.sidebar.multiselect("Type", types_available, default=types_available)

mask = (
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[-1])) &
    (df["category"].isin(selected_categories)) &
    (df["type"].isin(selected_types))
)
fdf = df[mask]

if fdf.empty:
    st.warning("No transactions match the current filters.")
    st.stop()

# ---------- Overview metrics ----------
stats = analytics.overall_stats(fdf)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Income", f"${stats['total_income']:,.2f}")
c2.metric("Total Expenses", f"${stats['total_expenses']:,.2f}")
c3.metric("Net", f"${stats['net']:,.2f}")
c4.metric("Savings Rate", f"{stats['savings_rate']:.1f}%")

st.divider()

# ---------- Monthly income vs expenses ----------
st.subheader("Income vs. Expenses by Month")
monthly = analytics.monthly_summary(fdf)
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(monthly["month"], monthly["income"], label="Income", alpha=0.8)
ax.bar(monthly["month"], monthly["expenses"], label="Expenses", alpha=0.8)
ax.set_ylabel("$")
ax.legend()
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

# ---------- Savings rate trend ----------
st.subheader("Savings Rate Trend")
fig2, ax2 = plt.subplots(figsize=(10, 3))
ax2.plot(monthly["month"], monthly["savings_rate"], marker="o")
ax2.axhline(0, color="gray", linewidth=0.8)
ax2.set_ylabel("Savings rate (%)")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig2)

col1, col2 = st.columns(2)

# ---------- Top categories ----------
with col1:
    st.subheader("Top Spending Categories")
    top_cats = analytics.top_categories(fdf)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.barh(top_cats["category"], top_cats["spend"])
    ax3.invert_yaxis()
    ax3.set_xlabel("$")
    st.pyplot(fig3)

# ---------- Month-over-month comparison ----------
with col2:
    st.subheader("Month-over-Month Change")
    mom = analytics.month_over_month(fdf)
    st.dataframe(
        mom[["month", "income", "expenses", "expenses_change_pct"]].rename(
            columns={"expenses_change_pct": "Δ expenses %"}
        ).round(1),
        use_container_width=True, hide_index=True
    )

# ---------- Spending trends by category over time ----------
st.subheader("Spending Trends by Category")
cat_month = analytics.category_by_month(fdf)
fig4, ax4 = plt.subplots(figsize=(10, 5))
for cat in cat_month.columns:
    ax4.plot(cat_month.index, cat_month[cat], marker="o", label=cat, linewidth=1)
ax4.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig4)

# ---------- Raw data ----------
with st.expander("View categorized transactions"):
    st.dataframe(
        fdf[["date", "description", "amount", "type", "category", "category_source"]]
        .sort_values("date", ascending=False),
        use_container_width=True, hide_index=True
    )
