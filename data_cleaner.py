import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Data loading
df = pd.read_csv("jumia_products.csv")
#Data info
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

# Remove null values
df_clean = df.dropna(subset=['name'])
print(f"After removing missing names: {df_clean.shape}")

# Remove duplicates
df_clean = df_clean.drop_duplicates(subset=['url'])
print(f"After removing duplicates: {df_clean.shape}")

# Turning prices to floats
df_clean['price'] = df_clean['price'].str.replace('Dhs', '', regex=False).str.replace(",", "", regex=False)

df_clean['price'] = df_clean['price'].apply(
    lambda x: (float(x.split(' - ')[0]) + float(x.split(' - ')[1])) / 2 if ' - ' in x else float(x)
)


df_clean['price'] = df_clean['price'].astype(float)

# Create new features
# Uncomment after adding discounts to scrapped data
# df_clean['Has_Discount'] = (df_clean['Discount %'] > 0).astype(int)


# To be modified when discounts added
price_bins = df_clean['price'].quantile([0, .25, .5, .75, 1]) # Categorizing data ensuring 25% of the data falls into each category
df_clean['Price_Category'] = pd.cut(df_clean['price'], 
                                      bins = price_bins, 
                                      labels = ['Low', 'Medium', 'High', 'Premium'],
                                      include_lowest = True
                                    )

# Handle missing old prices
# Uncomment after adding discounts to scrapped data
# df_clean['Old Price'] = df_clean['Old Price'].fillna(df_clean['Current Price'])


####### This is only because Jumia includes a mystery item with 100,000 Dhs set as its price ################

max_price_index = df_clean['price'].idxmax()

df_clean = df_clean.drop(max_price_index, axis=0)

print(f"\nRemoved 1 row with index {max_price_index} (price 100000.0).")
print(f"New maximum price: {df_clean['price'].max()}")

###############################################################################################################

print("\nCleaned data summary:")
print(df_clean.describe())
print(df_clean.head())

# ---------- Save cleaned data ----------
df_clean.to_csv("cleaned_jumia_products.csv", index=False)
print("\n✓ Cleaned data saved as: cleaned_jumia_products.csv")
