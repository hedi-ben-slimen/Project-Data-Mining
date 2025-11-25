import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("cleaned_jumia_products.csv")

print("="*60)
print("K-MEANS CLUSTERING - JUMIA PRODUCTS")
print("="*60)

features = ['price', 'discount_percent']
X = df[features].values

print(f"\nFeatures for clustering: {features}")
print(f"Data shape: {X.shape}")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\nData standardized (mean=0, std=1)")

print("\nFinding optimal number of clusters...")

inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (K)', fontsize=12)
plt.ylabel('Inertia (Within-cluster sum of squares)', fontsize=12)
plt.title('Elbow Method - Finding Optimal K', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.savefig('elbow_method.png', dpi=300, bbox_inches='tight')
print("✓ Elbow plot saved as: elbow_method.png")
plt.show()

optimal_k = 4  
print(f"\nApplying K-Means with K={optimal_k}")

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

print(f"✓ Clustering complete!")

print("\n" + "="*60)
print("CLUSTER ANALYSIS")
print("="*60)

for i in range(optimal_k):
    cluster_data = df[df['Cluster'] == i]
    print(f"\n--- Cluster {i} ---")
    print(f"Size: {len(cluster_data)} products ({len(cluster_data)/len(df)*100:.1f}%)")
    print(f"Avg Price: {cluster_data['price'].mean():.2f} Dhs")
    print(f"Avg Discount: {cluster_data['discount_percent'].mean():.2f}%")
    print(f"Price Range: {cluster_data['price'].min():.2f} - {cluster_data['price'].max():.2f} Dhs")
    print(f"Top Categories: {cluster_data['category'].value_counts().head(3).to_dict()}")

print("\n" + "="*60)
print("CLUSTER INTERPRETATION")
print("="*60)

cluster_summary = df.groupby('Cluster').agg({
    'price': ['mean', 'min', 'max'],
    'discount_percent': ['mean', 'max'],
    'name': 'count'
}).round(2)

cluster_summary.columns = ['Avg_Price', 'Min_Price', 'Max_Price', 'Avg_Discount', 'Max_Discount', 'Count']
print(cluster_summary)

cluster_labels = []
for i in range(optimal_k):
    avg_price = cluster_summary.loc[i, 'Avg_Price']
    avg_discount = cluster_summary.loc[i, 'Avg_Discount']
    
    if avg_price < 500 and avg_discount < 20:
        label = "Budget Products"
    elif avg_price < 500 and avg_discount >= 20:
        label = "Discounted Budget"
    elif avg_price >= 500 and avg_discount < 20:
        label = "Premium Products"
    else:
        label = "Premium on Sale"
    
    cluster_labels.append(label)
    print(f"\nCluster {i}: {label}")

df['Cluster_Label'] = df['Cluster'].map(dict(enumerate(cluster_labels)))

df.to_csv("clustered_jumia_products.csv", index=False)
print(f"\n✓ Clustered data saved as: clustered_jumia_products.csv")

print("\n✓ K-Means clustering complete!")