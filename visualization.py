import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# ---------- Load clustered data ----------
df = pd.read_csv("clustered_jumia_products.csv")

print("="*60)
print("JUMIA CLUSTER VISUALIZATION")
print("="*60)

# ---------- Static Visualizations with Seaborn ----------
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Scatter plot: Price vs Discount colored by cluster
scatter = axes[0, 0].scatter(df['price'], df['discount_percent'], 
                             c=df['Cluster'], cmap='viridis', 
                             s=100, alpha=0.6, edgecolors='black')
axes[0, 0].set_xlabel('Price (Dhs)', fontsize=12)
axes[0, 0].set_ylabel('Discount %', fontsize=12)
axes[0, 0].set_title('Clusters: Price vs Discount', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=axes[0, 0], label='Cluster')

# 2. Box plot: Price distribution by cluster
sns.boxplot(data=df, x='Cluster', y='price', palette='Set2', ax=axes[0, 1])
axes[0, 1].set_title('Price Distribution by Cluster', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Cluster', fontsize=12)
axes[0, 1].set_ylabel('Price (Dhs)', fontsize=12)

# 3. Count plot: Products per cluster
cluster_counts = df['Cluster'].value_counts().sort_index()
colors = sns.color_palette('viridis', n_colors=len(cluster_counts))
axes[1, 0].bar(cluster_counts.index, cluster_counts.values, color=colors, edgecolor='black')
axes[1, 0].set_title('Number of Products per Cluster', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Cluster', fontsize=12)
axes[1, 0].set_ylabel('Number of Products', fontsize=12)

# Add count labels on bars
for i, v in enumerate(cluster_counts.values):
    axes[1, 0].text(i, v + 5, str(v), ha='center', fontweight='bold')

# 4. Heatmap: Average features by cluster
cluster_summary = df.groupby('Cluster')[['price', 'discount_percent', 'Has_Discount']].mean()
sns.heatmap(cluster_summary.T, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[1, 1], cbar_kws={'label': 'Value'})
axes[1, 1].set_title('Average Features by Cluster', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Cluster', fontsize=12)

plt.tight_layout()
plt.savefig('seaborn_clusters.png', dpi=300, bbox_inches='tight')
print("✓ Seaborn visualizations saved as: seaborn_clusters.png")
plt.show()

# ---------- Interactive Visualizations with Plotly ----------
print("\nCreating interactive Plotly visualizations...")

# 1. Interactive Scatter Plot
fig1 = px.scatter(df, 
                  x='price', 
                  y='discount_percent',
                  color='Cluster_Label',
                  size='price',
                  hover_data=['name', 'category', 'old_price'],
                  title='Interactive Jumia Product Clusters',
                  labels={'price': 'Price (Dhs)', 'discount_percent': 'Discount (%)'},
                  color_discrete_sequence=px.colors.qualitative.Set2)

fig1.update_layout(height=600, font=dict(size=12))
fig1.write_html('plotly_scatter.html')
print("✓ Interactive scatter plot saved as: plotly_scatter.html")
fig1.show()

# 2. 3D Scatter Plot
fig2 = px.scatter_3d(df,
                     x='price',
                     y='discount_percent',
                     z='old_price',
                     color='Cluster_Label',
                     hover_data=['name', 'category'],
                     title='3D Jumia Product Clusters',
                     labels={'price': 'Current Price (Dhs)', 
                             'discount_percent': 'Discount (%)',
                             'old_price': 'Old Price (Dhs)'},
                     color_discrete_sequence=px.colors.qualitative.Bold)

fig2.update_layout(height=700)
fig2.write_html('plotly_3d_scatter.html')
print("✓ 3D scatter plot saved as: plotly_3d_scatter.html")
fig2.show()

# 3. Box Plot by Category and Cluster
fig3 = px.box(df, 
              x='Cluster_Label', 
              y='price',
              color='Cluster_Label',
              title='Price Distribution by Cluster',
              labels={'price': 'Price (Dhs)', 'Cluster_Label': 'Cluster Type'},
              color_discrete_sequence=px.colors.qualitative.Pastel)

fig3.update_layout(height=500, showlegend=False)
fig3.write_html('plotly_boxplot.html')
print("✓ Box plot saved as: plotly_boxplot.html")
fig3.show()

# 4. Sunburst Chart: Category -> Cluster hierarchy
category_cluster = df.groupby(['category', 'Cluster_Label']).size().reset_index(name='count')
fig4 = px.sunburst(category_cluster,
                   path=['category', 'Cluster_Label'],
                   values='count',
                   title='Product Distribution: Category → Cluster',
                   color='count',
                   color_continuous_scale='Viridis')

fig4.update_layout(height=700)
fig4.write_html('plotly_sunburst.html')
print("✓ Sunburst chart saved as: plotly_sunburst.html")
fig4.show()

# 5. Category Distribution by Cluster
fig5 = go.Figure()

for cluster_label in df['Cluster_Label'].unique():
    cluster_data = df[df['Cluster_Label'] == cluster_label]
    category_counts = cluster_data['category'].value_counts().head(5)
    
    fig5.add_trace(go.Bar(
        name=cluster_label,
        x=category_counts.index,
        y=category_counts.values
    ))

fig5.update_layout(
    title='Top 5 Categories per Cluster',
    xaxis_title='Category',
    yaxis_title='Number of Products',
    barmode='group',
    height=500
)
fig5.write_html('plotly_category_distribution.html')
print("✓ Category distribution saved as: plotly_category_distribution.html")
fig5.show()

print("\n✓ All visualizations created successfully!")