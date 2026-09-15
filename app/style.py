"""
Visual design system for the dashboard: a shared palette + typography so
the CSS injected into Streamlit and the matplotlib charts actually match,
instead of native Streamlit grey next to default matplotlib blue/orange.
"""
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---- Palette ----
INK = "#16202B"        # primary text / headlines
SLATE = "#5B6B7C"       # secondary text, axis labels
BORDER = "#E2E6EA"      # hairlines
CANVAS = "#FFFFFF"      # page background
PANEL = "#F5F7F9"       # sidebar / panel background

INCOME = "#1F9D7C"      # teal -- money in
EXPENSE = "#E0913F"     # amber -- money out
NET = "#2C4A7C"         # muted navy -- net / neutral series
NEGATIVE = "#C0483D"    # muted brick red -- only for negative net, sparingly

CATEGORY_PALETTE = [
    "#1F9D7C", "#2C4A7C", "#E0913F", "#7C5CBF", "#3E8FB0",
    "#C0483D", "#5B6B7C", "#9CB380", "#B5854B", "#5C7A99",
]

FONT_STACK = "'Inter', -apple-system, 'Segoe UI', sans-serif"


def inject_css():
    import streamlit as st
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: {FONT_STACK};
        color: {INK};
    }}

    /* Remove Streamlit's default top padding so the header sits higher */
    .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}

    /* Page title */
    h1 {{
        font-weight: 700;
        font-size: 1.9rem;
        letter-spacing: -0.01em;
        color: {INK};
        margin-bottom: 0.1rem;
    }}

    h2, h3 {{
        font-weight: 600;
        color: {INK};
        letter-spacing: -0.005em;
    }}

    /* Caption under the title */
    [data-testid="stCaptionContainer"] {{
        color: {SLATE};
        font-size: 0.95rem;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {PANEL};
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {SLATE};
        text-transform: none;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background-color: {CANVAS};
        border: 1px solid {BORDER};
        border-left: 3px solid {NET};
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
    }}
    div[data-testid="stMetric"] label {{
        color: {SLATE};
        font-weight: 500;
        font-size: 0.85rem;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {INK};
        font-weight: 700;
    }}

    /* Dataframes */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 6px;
    }}

    /* Section divider look: quiet hairlines, not boxed cards */
    hr {{
        border-color: {BORDER};
        margin: 1.6rem 0;
    }}

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {PANEL};
        border: 1px dashed {BORDER};
    }}

    /* Buttons */
    .stButton button {{
        border-radius: 6px;
        border: 1px solid {BORDER};
        font-weight: 500;
    }}
    </style>
    """, unsafe_allow_html=True)


def apply_matplotlib_style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica", "Arial"],
        "text.color": INK,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": SLATE,
        "axes.titlecolor": INK,
        "axes.titleweight": "600",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": BORDER,
        "grid.linewidth": 0.8,
        "xtick.color": SLATE,
        "ytick.color": SLATE,
        "figure.facecolor": CANVAS,
        "axes.facecolor": CANVAS,
        "legend.frameon": False,
    })
