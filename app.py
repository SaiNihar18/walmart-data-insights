import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

# Page configuration
st.set_page_config(
    page_title="Walmart Sales Insights Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium design and fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom Card Style */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        text-align: center;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a; /* Navy */
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b; /* Slate Gray */
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Header gradients */
    .dashboard-title {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    
    /* Subheaders */
    .dashboard-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load datasets safely
@st.cache_data
def load_cleaned_data():
    if os.path.exists('walmart_cleaned.csv'):
        df = pd.read_csv('walmart_cleaned.csv')
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        return df
    return None

@st.cache_data
def load_clustered_data():
    if os.path.exists('walmart_clustered_branches.csv'):
        return pd.read_csv('walmart_clustered_branches.csv')
    return None

@st.cache_data
def load_forecast_data():
    if os.path.exists('walmart_forecast_eval.csv'):
        df = pd.read_csv('walmart_forecast_eval.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None


df_sales = load_cleaned_data()
df_clustered = load_clustered_data()
df_forecast = load_forecast_data()

# Navigation Sidebar
st.sidebar.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Walmart Data Portal</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Choose Analysis View",
    ["📊 Executive Overview", "📈 Sales Forecasting", "🏷️ Market Segments", "🎯 Price Elasticity Simulator"]
)

# ----------------- PAGE 1: EXECUTIVE OVERVIEW -----------------
if page == "📊 Executive Overview":
    st.markdown("<h1 class='dashboard-title'>Walmart Executive Sales Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>Interactive descriptive analytics of sales transactions (2019-2023)</p>", unsafe_allow_html=True)
    
    if df_sales is None:
        st.error("Dataset 'walmart_cleaned.csv' not found. Please run your ETL pipeline first.")
    else:
        # Filters
        st.sidebar.markdown("### Dashboard Filters")
        
        # Date filter — safely handle single date or range tuple
        min_date, max_date = df_sales['date'].min(), df_sales['date'].max()
        date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
        
        # Category filter
        categories = df_sales['category'].unique().tolist()
        selected_categories = st.sidebar.multiselect("Product Category", categories, default=categories)
        
        # Payment method filter
        payments = df_sales['payment_method'].unique().tolist()
        selected_payments = st.sidebar.multiselect("Payment Method", payments, default=payments)
        
        # Filter Data
        mask = (
            (df_sales['date'] >= pd.to_datetime(start_date)) & 
            (df_sales['date'] <= pd.to_datetime(end_date)) & 
            (df_sales['category'].isin(selected_categories)) &
            (df_sales['payment_method'].isin(selected_payments))
        )
        filtered_df = df_sales[mask]
        
        # Metric columns
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate values
        if filtered_df.empty:
            st.warning("No data matches the selected filters. Please adjust your selections.")
            st.stop()
        total_sales = filtered_df['total'].sum()
        total_profit = (filtered_df['unit_price'] * filtered_df['quantity'] * filtered_df['profit_margin']).sum()
        avg_rating = filtered_df['rating'].mean()
        num_transactions = len(filtered_df)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${total_sales:,.2f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${total_profit:,.2f}</div>
                <div class="metric-label">Estimated Profit</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_rating:.2f} ★</div>
                <div class="metric-label">Average Rating</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{num_transactions:,}</div>
                <div class="metric-label">Transactions</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Charts section
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("### Monthly Sales Trends")
            monthly_sales = filtered_df.resample('ME', on='date')['total'].sum().reset_index()
            fig_monthly = px.line(
                monthly_sales, x='date', y='total', 
                labels={'total': 'Revenue ($)', 'date': 'Month'},
                color_discrete_sequence=['#3b82f6']
            )
            fig_monthly.update_traces(line=dict(width=3), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)')
            fig_monthly.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                xaxis_title="",
                yaxis_title=""
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        with c2:
            st.markdown("### Payment Method Share")
            payment_share = filtered_df.groupby('payment_method')['total'].sum().reset_index()
            fig_pie = px.pie(
                payment_share, values='total', names='payment_method',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(hole=0.4)
            fig_pie.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("### Revenue by Product Category")
        cat_sales = filtered_df.groupby('category')['total'].sum().reset_index().sort_values('total', ascending=True)
        fig_cat = px.bar(
            cat_sales, x='total', y='category', orientation='h',
            labels={'total': 'Revenue ($)', 'category': 'Category'},
            color='total', color_continuous_scale='Blues'
        )
        fig_cat.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            xaxis_title="",
            yaxis_title=""
        )
        st.plotly_chart(fig_cat, use_container_width=True)

# ----------------- PAGE 2: SALES FORECASTING -----------------
elif page == "📈 Sales Forecasting":
    st.markdown("<h1 class='dashboard-title'>Product Category Demand Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>Compare actual sales vs XGBoost predictions for the validation year (2023)</p>", unsafe_allow_html=True)
    
    if df_forecast is None:
        st.error("Forecast evaluation data 'walmart_forecast_eval.csv' not found. Please run your modeling pipeline first.")
    else:
        # Get category list by looking for cat_ dummy columns
        dummy_cols = [c for c in df_forecast.columns if c.startswith('cat_')]
        categories = [c.replace('cat_', '') for c in dummy_cols]
        
        selected_cat = st.selectbox("Select Product Category to Forecast", categories)
        
        # Map selected category back to dummy column
        cat_dummy = f"cat_{selected_cat}"
        
        # Filter evaluation data
        cat_mask = df_forecast[cat_dummy] == 1
        df_cat_forecast = df_forecast[cat_mask].sort_values('date')
        
        # Metrics
        y_true = df_cat_forecast['weekly_sales']
        y_pred = df_cat_forecast['predicted_sales']
        
        rmse = np.sqrt(np.mean((y_true - y_pred)**2))
        mape = np.mean(np.abs((y_true - y_pred) / y_true))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${df_cat_forecast['weekly_sales'].sum():,.2f}</div>
                <div class="metric-label">Total Actual Sales (2023)</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${rmse:.2f}</div>
                <div class="metric-label">Root Mean Squared Error (RMSE)</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{mape:.2%}</div>
                <div class="metric-label">Mean Absolute % Error (MAPE)</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Plotting actual vs forecast
        st.markdown(f"### Weekly Sales: Actual vs. Forecasted ({selected_cat})")
        fig_fore = go.Figure()
        fig_fore.add_trace(go.Scatter(
            x=df_cat_forecast['date'], y=df_cat_forecast['weekly_sales'],
            name="Actual Weekly Sales", line=dict(color="#1e293b", width=2.5)
        ))
        fig_fore.add_trace(go.Scatter(
            x=df_cat_forecast['date'], y=df_cat_forecast['predicted_sales'],
            name="XGBoost Prediction", line=dict(color="#ef4444", width=2.5, dash='dash')
        ))
        fig_fore.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="Date",
            yaxis_title="Sales Revenue ($)"
        )
        st.plotly_chart(fig_fore, use_container_width=True)

# ----------------- PAGE 3: MARKET SEGMENTS -----------------
elif page == "🏷️ Market Segments":
    st.markdown("<h1 class='dashboard-title'>Branch Market Segmentation</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>Profiling the 100 Walmart branches using K-Means Clustering on financial KPIs & product mix</p>", unsafe_allow_html=True)
    
    if df_clustered is None:
        st.error("Clustering dataset 'walmart_clustered_branches.csv' not found. Please run your modeling pipeline first.")
    else:
        # Show cluster profile explanation
        st.markdown("### Branch Performance Clusters Profile")
        
        # Calculate cluster summaries
        cluster_summary = df_clustered.groupby('cluster').agg(
            num_branches=('Branch', 'count'),
            avg_revenue=('total_revenue', 'mean'),
            avg_rating=('avg_rating', 'mean'),
            avg_margin=('avg_profit_margin', 'mean')
        ).reset_index()
        
        # Custom descriptions based on cluster averages
        descriptions = []
        for idx, row in cluster_summary.iterrows():
            rev = row['avg_revenue']
            rating = row['avg_rating']
            if rev > 13000:
                descriptions.append("🏆 High-Volume Powerhouses (Dominant sales volume & solid ratings)")
            elif rating > 7.1:
                descriptions.append("⭐ High-Satisfaction Outlets (Excellent customer feedback & ratings)")
            elif rev < 10000:
                descriptions.append("📉 Small-Market Outlets (Low overall revenue, serving smaller communities)")
            else:
                descriptions.append("⚖️ Balanced Mid-Tier (Average revenue, steady margins)")
                
        cluster_summary['Profile Description'] = descriptions
        
        # Print profiles
        for idx, row in cluster_summary.iterrows():
            st.info(f"**Cluster {int(row['cluster'])}**: {row['Profile Description']}  \n"
                    f"  * Branches: **{int(row['num_branches'])}** | "
                    f"Average Branch Revenue: **${row['avg_revenue']:,.2f}** | "
                    f"Average Customer Rating: **{row['avg_rating']:.2f} / 10**")
            
        # Scatter Plot
        st.markdown("### Cluster Visualizer: Branch Revenue vs. Customer Rating")
        df_clustered['cluster_name'] = df_clustered['cluster'].apply(lambda x: f"Cluster {x}")
        
        fig_scatter = px.scatter(
            df_clustered, x='avg_rating', y='total_revenue', 
            color='cluster_name', size='total_quantity', hover_name='Branch',
            labels={'avg_rating': 'Average Rating', 'total_revenue': 'Total Branch Revenue ($)'},
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_scatter.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            legend_title_text="Cohort Cluster"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------- PAGE 4: PRICE ELASTICITY SIMULATOR -----------------
elif page == "🎯 Price Elasticity Simulator":
    st.markdown("<h1 class='dashboard-title'>What-If Price Elasticity Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>Simulate pricing adjustment impacts on sales volume and total revenue using category elasticity coefficients</p>", unsafe_allow_html=True)
    
    if df_sales is None:
        st.error("Cleaned sales data 'walmart_cleaned.csv' not found. Please run your ETL pipeline first.")
    else:
        # Predefined elasticity coefficients for product categories based on standard retail benchmarks
        elasticities = {
            "Food and beverages": -0.85,     # Inelastic (Necessity)
            "Health and beauty": -1.20,      # Moderately elastic
            "Home and lifestyle": -1.40,     # Elastic
            "Fashion accessories": -1.65,    # Highly elastic (Discretionary)
            "Electronic accessories": -1.80, # Highly elastic
            "Sports and travel": -1.50       # Elastic
        }
        
        st.sidebar.markdown("### Simulation Parameters")
        category = st.sidebar.selectbox("Select Product Category", list(elasticities.keys()))
        price_change = st.sidebar.slider("Change Price (%)", min_value=-20, max_value=20, value=0, step=1)
        
        # Current status
        cat_df = df_sales[df_sales['category'] == category]
        avg_price = cat_df['unit_price'].mean()
        total_qty = cat_df['quantity'].sum()
        current_rev = cat_df['total'].sum()
        
        # Calculate simulations
        coef = elasticities[category]
        pct_price_change = price_change / 100.0
        pct_qty_change = pct_price_change * coef
        
        proj_price = avg_price * (1 + pct_price_change)
        proj_qty = total_qty * (1 + pct_qty_change)
        proj_rev = current_rev * (1 + pct_price_change) * (1 + pct_qty_change)
        
        rev_diff = proj_rev - current_rev
        qty_diff = proj_qty - total_qty
        
        # Display coefficients
        st.markdown(f"#### Category Benchmark: **{category}**")
        st.info(f"Price Elasticity Coefficient ($\epsilon$): **{coef}**  \n"
                f"A **1% price increase** yields a **{abs(coef):.2f}% demand reduction**. "
                f"Since $|\epsilon| {' > 1$ (Elastic)' if abs(coef) > 1 else ' < 1$ (Inelastic)'}, "
                f"demand is {'highly sensitive' if abs(coef) > 1 else 'relatively insensitive'} to price changes.")
        
        # Display Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            delta_p = f"{price_change:+.0f}%" if price_change != 0 else "0%"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${proj_price:.2f}</div>
                <div class="metric-label">Projected Avg Price (Delta: {delta_p})</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            pct_q_str = f"{pct_qty_change*100:+.2f}%" if price_change != 0 else "0%"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(proj_qty):,} items</div>
                <div class="metric-label">Projected Sales Qty (Delta: {pct_q_str})</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            pct_r_str = f"{(proj_rev - current_rev)/current_rev*100:+.2f}%" if price_change != 0 else "0%"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${proj_rev:,.2f}</div>
                <div class="metric-label">Projected Revenue (Delta: {pct_r_str})</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Chart: Comparison
        st.markdown("### Revenue Impact: Current vs. Projected")
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(
            x=['Current Revenue', 'Projected Revenue'],
            y=[current_rev, proj_rev],
            marker_color=['#64748b', '#3b82f6' if rev_diff >= 0 else '#ef4444'],
            width=0.4
        ))
        
        # Format axes
        fig_sim.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title="Revenue ($)"
        )
        st.plotly_chart(fig_sim, use_container_width=True)
