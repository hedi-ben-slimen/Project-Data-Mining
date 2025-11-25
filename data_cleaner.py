import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("jumia_products.csv")

print(f"Initial shape: {df.shape}")
print("\nFirst rows:")
print(df.head())
print("\nData info:")
print(df.info())
print("\nMissing values:")
print(df.isnull().sum())

print("\n" + "="*60)
print("STEP 1: Data Cleaning")
print("="*60)

df_clean = df.dropna(subset=['name'])
print(f"After removing missing names: {df_clean.shape}")

df_clean = df_clean.drop_duplicates(subset=['url'])
print(f"After removing duplicates: {df_clean.shape}")

df_clean['price'] = df_clean['price'].str.replace('Dhs', '', regex=False).str.replace(",", "", regex=False)

df_clean['price'] = df_clean['price'].apply(
    lambda x: (float(x.split(' - ')[0]) + float(x.split(' - ')[1])) / 2 if ' - ' in x else float(x)
)

df_clean['price'] = df_clean['price'].astype(float)

df_clean['old_price'] = df_clean['old_price'].fillna(df_clean['price'])
df_clean['old_price'] = df_clean['old_price'].str.replace('Dhs', '', regex=False).str.replace(",", "", regex=False)

df_clean['old_price'] = df_clean['old_price'].apply(
    lambda x: (float(x.split(' - ')[0]) + float(x.split(' - ')[1])) / 2 if ' - ' in str(x) else float(x)
)

df_clean['old_price'] = df_clean['old_price'].astype(float)

df_clean['discount_percent'] = pd.to_numeric(df_clean['discount_percent'], errors='coerce').fillna(0)

df_clean['Has_Discount'] = (df_clean['discount_percent'] > 0).astype(int)

price_bins = df_clean['price'].quantile([0, .25, .5, .75, 1])
df_clean['Price_Category'] = pd.cut(df_clean['price'], 
                                      bins=price_bins, 
                                      labels=['Low', 'Medium', 'High', 'Premium'],
                                      include_lowest=True)

max_price_index = df_clean['price'].idxmax()

if df_clean.loc[max_price_index, 'price'] > 50000: 
    df_clean = df_clean.drop(max_price_index, axis=0)
    print(f"\nRemoved 1 row with index {max_price_index} (price {df_clean['price'].max()}).")

print(f"New maximum price: {df_clean['price'].max()}")

print("\nCleaned data summary:")
print(df_clean.describe())
print("\nFirst rows of cleaned data:")
print(df_clean.head())

print("\nDiscount statistics:")
print(f"Products with discounts: {df_clean['Has_Discount'].sum()}")
print(f"Average discount percentage: {df_clean[df_clean['Has_Discount'] == 1]['discount_percent'].mean():.2f}%")

df_clean.to_csv("cleaned_jumia_products.csv", index=False)
print("\n✓ Cleaned data saved as: cleaned_jumia_products.csv")