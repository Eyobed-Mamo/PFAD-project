"""
Trains a transaction categorization model.

Approach: TF-IDF over character n-grams of the transaction description,
feeding a Logistic Regression classifier. Character n-grams (not just word
tokens) matter here because real bank descriptions are often truncated /
concatenated merchant strings (e.g. "AMZN MKTP US*2K3", "SQ *THAI TAVERN").
Word-level TF-IDF would fail on those; char n-grams pick up on substrings
like "amzn" or "sq *" regardless of surrounding noise.
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

df = pd.read_csv('data/clean_transactions.csv')

X = df['Description'].str.lower()
y = df['Category']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), min_df=1)),
    ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {acc:.3f}")
print()
print(classification_report(y_test, y_pred, zero_division=0))

# Also report accuracy on unique/unseen-style descriptions to be honest about
# what this number really means (the dataset repeats ~65 merchants a lot,
# so a naive split can look artificially strong).
unique_desc = df.drop_duplicates(subset='Description')
Xu = unique_desc['Description'].str.lower()
yu = unique_desc['Category']
acc_unique = accuracy_score(yu, pipeline.predict(Xu))
print(f"Accuracy on the 65 distinct merchant strings: {acc_unique:.3f}")

with open('models/categorizer_model.pkl', 'wb') as f:
    pickle.dump(pipeline, f)

with open('models/model_metrics.txt', 'w') as f:
    f.write(f"Test accuracy: {acc:.3f}\n")
    f.write(f"Accuracy on distinct merchant strings: {acc_unique:.3f}\n")
    f.write(f"Train size: {len(X_train)}, Test size: {len(X_test)}\n")
    f.write(f"Classes: {sorted(y.unique())}\n")

print("\nModel saved to models/categorizer_model.pkl")
