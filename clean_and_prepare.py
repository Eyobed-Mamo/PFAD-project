import pandas as pd
import numpy as np

df = pd.read_excel('data/set2/personal_transactions_dashboard_ready (2).xlsx')

# Merge ultra-rare classes (<5 samples) into a catch-all so the model has enough
# examples per class to learn something meaningful, and stratified splits work.
counts = df['Category'].value_counts()
rare = counts[counts < 5].index.tolist()
print("Merging rare categories into 'Other':", rare)
df['Category'] = df['Category'].apply(lambda c: 'Other' if c in rare else c)

# Normalize sign of Amount: debit = money out (negative), credit = money in (positive)
df['Amount'] = df.apply(
    lambda r: -abs(r['Amount']) if r['Transaction Type'] == 'debit' else abs(r['Amount']),
    axis=1
)

df = df.rename(columns={'Transaction Type': 'Type'})
df['Type'] = df['Type'].map({'debit': 'Expense', 'credit': 'Income'})

df.to_csv('data/clean_transactions.csv', index=False)
print(df.shape)
print(df['Category'].value_counts())
print(df.head())
