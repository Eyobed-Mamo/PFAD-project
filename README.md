# Personal Finance Analytics Dashboard

Upload a bank transaction CSV and get automatic categorization (via a trained
ML classifier, not hardcoded rules) plus a full spending analysis: income vs.
expenses, savings rate, monthly trends, top categories, and month-over-month
comparisons.

## How it works

**1. Categorization model** (`train_model.py`)
Trained on a labeled dataset of ~800 real-world-style transactions (merchant
name → category). Uses TF-IDF over *character* n-grams rather than word
tokens, since real bank statement descriptions are often truncated or
concatenated (`AMZN MKTP US*2K3`, `SQ *THAI TAVERN`) — character n-grams pick
up on recognizable substrings regardless of the surrounding noise. Feeds a
Logistic Regression classifier.

- Test accuracy: 93.8%
- Accuracy on the 65 distinct merchant strings in the dataset (a more honest
  number, since the test-set accuracy is inflated by repeated merchants):
  80%
- Low-confidence predictions are flagged as "Uncategorized" rather than
  forced into a guess — see `categorizer.py`

**2. Ingestion pipeline** (`categorizer.py`)
Normalizes whatever column names/casing a bank export uses (`Transaction
Date` vs `Date`, `Merchant` vs `Description`, etc.), infers income vs.
expense from a type column if present or from the sign of the amount if not,
and standardizes everything into one schema.

**3. Storage** (`db.py`)
SQLite. Each upload is tagged with a batch ID so multiple statements can be
loaded and analyzed together over time.

**4. Analytics** (`analytics.py`)
Pure pandas functions — monthly income/expense/savings rate, top spending
categories, category trends over time, month-over-month % change. Kept
separate from the UI so they're independently testable.

**5. App** (`app.py`)
Streamlit front end with CSV upload, interactive filters (date range,
category, type), and matplotlib visualizations.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Try it with `sample_data/sample_transactions.csv` — a raw, uncategorized
export with no category column, so you can see the model do its job.

## Tech stack
Python, pandas, scikit-learn, SQLite, Streamlit, Matplotlib

## Known limitations
- The training data is a public dataset of ~800 transactions across 65
  distinct merchants — solid for a portfolio project, but a production
  system would want a much larger and more diverse merchant vocabulary.
- Category set is fixed to what's in the training data. A merchant type the
  model has never seen will fall into whatever category its description
  most closely resembles, or get flagged "Uncategorized" if the model isn't
  confident.
