import pkgutil
import importlib.util

if not hasattr(pkgutil, "find_loader"):
    pkgutil.find_loader = importlib.util.find_spec

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ---------- Load data ----------
df = pd.read_csv("clustered_jumia_products.csv")

# ---------- Initialize Dash App ----------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ---------- App Layout ----------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🛒 Jumia Morocco Product Clustering Dashboard", 
                   className="text-center text-primary mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Products", className="card-title"),
                    html.H2(f"{len(df)}", className="text-primary")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Avg Price", className="card-title"),
                    html.H2(f"{df['price'].mean():.2f} Dhs", className="text-success")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Products on Sale", className="card-title"),
                    html.H2(f"{df['Has_Discount'].sum()}", className="text-danger")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Clusters", className="card-title"),
                    html.H2(f"{df['Cluster'].nunique()}", className="text-info")
                ])
            ])
        ], width=3),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Cluster:", className="fw-bold"),
            dcc.Dropdown(
                id='cluster-dropdown',
                options=[{'label': 'All Clusters', 'value': 'all'}] + 
                        [{'label': f"Cluster {i}: {label}", 'value': i} 
                         for i, label in enumerate(df['Cluster_Label'].unique())],
                value='all',
                clearable=False
            )
        ], width=6),
        
        dbc.Col([
            html.Label("Select Category:", className="fw-bold"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': 'All Categories', 'value': 'all'}] + 
                        [{'label': cat, 'value': cat} for cat in sorted(df['category'].unique())],
                value='all',
                clearable=False
            )
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='scatter-plot')
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id='box-plot')
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart')
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id='pie-chart')
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.H4("Cluster Statistics", className="text-center mb-3"),
            html.Div(id='cluster-stats')
        ])
    ])
    
], fluid=True)

# ---------- Callbacks ----------
@callback(
    [Output('scatter-plot', 'figure'),
     Output('box-plot', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('cluster-stats', 'children')],
    [Input('cluster-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_dashboard(selected_cluster, selected_category):
    # Filter data
    filtered_df = df.copy()
    
    if selected_cluster != 'all':
        filtered_df = filtered_df[filtered_df['Cluster'] == selected_cluster]
    
    if selected_category != 'all':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # 1. Scatter Plot
    scatter_fig = px.scatter(filtered_df,
                            x='price',
                            y='discount_percent',
                            color='Cluster_Label',
                            size='price',
                            hover_data=['name', 'category'],
                            title='Price vs Discount by Cluster',
                            labels={'price': 'Price (Dhs)', 'discount_percent': 'Discount (%)'},
                            color_discrete_sequence=px.colors.qualitative.Set2)
    scatter_fig.update_layout(height=400)
    
    # 2. Box Plot
    box_fig = px.box(filtered_df,
                     x='Cluster_Label',
                     y='price',
                     color='Cluster_Label',
                     title='Price Distribution by Cluster',
                     labels={'price': 'Price (Dhs)', 'Cluster_Label': 'Cluster Type'},
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    box_fig.update_layout(height=400, showlegend=False)
    
    # 3. Bar Chart
    cluster_counts = filtered_df['Cluster_Label'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    bar_fig = px.bar(cluster_counts,
                     x='Cluster',
                     y='Count',
                     title='Products per Cluster',
                     color='Count',
                     color_continuous_scale='Viridis')
    bar_fig.update_layout(height=400)
    
    # 4. Pie Chart
    discount_counts = filtered_df['Has_Discount'].value_counts().reset_index()
    discount_counts.columns = ['Has Discount', 'Count']
    discount_counts['Has Discount'] = discount_counts['Has Discount'].map({1: 'On Sale', 0: 'Regular Price'})
    pie_fig = px.pie(discount_counts,
                     values='Count',
                     names='Has Discount',
                     title='Products on Sale vs Regular Price',
                     color_discrete_sequence=['#ff7f0e', '#1f77b4'])
    pie_fig.update_layout(height=400)
    
    # 5. Statistics Table
    stats = filtered_df.groupby('Cluster_Label').agg({
        'name': 'count',
        'price': ['mean', 'min', 'max'],
        'discount_percent': 'mean'
    }).round(2)
    
    stats.columns = ['Count', 'Avg Price', 'Min Price', 'Max Price', 'Avg Discount']
    
    table = dbc.Table.from_dataframe(
        stats.reset_index(),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="table-sm"
    )
    
    return scatter_fig, box_fig, bar_fig, pie_fig, table

# ---------- Run App ----------
if __name__ == '__main__':
    print("\n" + "="*60)
    print(" Starting Jumia Dashboard...")
    print("="*60)
    print(" Dashboard running at: http://127.0.0.1:8050")
    print(" Press CTRL+C to stop\n")
    app.run(debug=False, dev_tools_ui=False, dev_tools_props_check=False)