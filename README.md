# Personal Finance Analytics Dashboard

Upload a bank transaction CSV and the app categorizes every transaction with a trained ML model, not hardcoded rules. Then it shows you where your money goes: income vs. expenses, savings rate, monthly trends, top categories, and month-over-month changes.

## How it works

**Categorization model** (`train_model.py`)
Trained on about 800 labeled transactions. Bank descriptions are often cut off or mashed together (`AMZN MKTP US*2K3`, `SQ *THAI TAVERN`), so I used TF-IDF on character n-grams instead of whole words. That way the model picks up on recognizable pieces of a merchant name even when the rest is noise. A logistic regression classifier sits on top.

- 93.8% test accuracy
- 80% accuracy on the 65 distinct merchants in the data. This is the more honest number, since the test score is inflated by merchants that repeat.
- Low-confidence predictions are labeled "Uncategorized" instead of forcing a guess

**Ingestion** (`categorizer.py`)
Handles different column names from different banks (`Transaction Date` vs `Date`, `Merchant` vs `Description`). It figures out income vs. expense from a type column, or from the sign of the amount if there isn't one.

**Storage** (`db.py`)
SQLite. Each upload gets a batch ID, so you can load several statements and analyze them together.

**Analytics** (`analytics.py`)
Plain pandas functions, kept separate from the UI so they're easy to test.

**App** (`app.py`)
Streamlit front end with CSV upload, filters for date, category, and type, and Matplotlib charts.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Try it with `sample_data/sample_transactions.csv`. It has no category column, so you can watch the model categorize everything from scratch.

## Tech stack

Python, pandas, scikit-learn, SQLite, Streamlit, Matplotlib

## Limitations

- The model only knows about 65 distinct merchants. That's fine for a portfolio project, but a real system would need far more.
- The category list is fixed to what's in the training data. A merchant it hasn't seen gets the closest match, or "Uncategorized" if the model isn't confident.
