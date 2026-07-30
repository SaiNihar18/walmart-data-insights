import os
import pandas as pd
import numpy as np
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import root_mean_squared_error, mean_absolute_percentage_error
import joblib

# Set up logging
logger = logging.getLogger(__name__)

def segment_branches(df: pd.DataFrame, n_clusters: int = 4):
    """
    Groups the 100 Walmart branches into performance cohorts using K-Means clustering.
    Returns:
        kmeans_model: Trained K-Means estimator.
        scaler: Fitted StandardScaler.
        clustered_branches_df: DataFrame containing branch KPIs, category revenue shares, and cluster labels.
    """
    logger.info("Starting Branch Clustering pipeline.")
    
    # 1. Aggregate KPIs by branch
    branch_kpis = df.groupby('Branch').agg(
        total_revenue=('total', 'sum'),
        avg_transaction_val=('total', 'mean'),
        avg_profit_margin=('profit_margin', 'mean'),
        avg_rating=('rating', 'mean'),
        total_quantity=('quantity', 'sum')
    )
    
    # 2. Pivot category sales to calculate category sales share per branch
    cat_pivot = df.pivot_table(
        index='Branch',
        columns='category',
        values='total',
        aggfunc='sum',
        fill_value=0
    )
    
    # Normalize rows to get relative category share (sums to 1.0)
    category_shares = cat_pivot.div(cat_pivot.sum(axis=1), axis=0)
    # Rename columns to avoid collision and clarify they are shares
    category_shares = category_shares.rename(columns=lambda c: f"share_{c.lower().replace(' ', '_')}")
    
    # Combine KPIs and category shares
    features_df = branch_kpis.join(category_shares)
    
    # 3. Standardize features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    
    # 4. Fit K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_features)
    
    # Combine back
    clustered_df = features_df.copy()
    clustered_df['cluster'] = cluster_labels
    clustered_df = clustered_df.reset_index()
    
    logger.info(f"K-Means Branch Clustering complete. Grouped {len(clustered_df)} branches into {n_clusters} clusters.")
    # Log cluster sizes
    for c in range(n_clusters):
        size = np.sum(cluster_labels == c)
        logger.info(f"  Cluster {c}: {size} branches")
        
    return kmeans, scaler, clustered_df


def forecast_weekly_sales(df: pd.DataFrame):
    """
    Trains a weekly sales forecasting model for product categories using XGBoost.
    Uses lag features, calendar features, and rolling windows.
    Returns:
        model: Trained XGBRegressor.
        feature_cols: List of features used in training.
        test_df: DataFrame with test actuals, predictions, and date indices.
        metrics: Dictionary containing RMSE and MAPE.
    """
    logger.info("Starting Weekly Sales Forecasting pipeline.")
    
    # Ensure dates are datetime
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'], dayfirst=True)
    
    # 1. Aggregate to weekly sales per product category
    # W-MON aggregates weekly ending on Mondays
    weekly_sales = (
        df_copy.groupby(['category', pd.Grouper(key='date', freq='W')])
        .agg(weekly_sales=('total', 'sum'))
        .reset_index()
    )
    
    # 2. Build time-series features for each category individually to prevent cross-leakage
    feature_dfs = []
    for cat, group in weekly_sales.groupby('category'):
        group = group.sort_values('date').copy()
        
        # Lags
        group['lag_1'] = group['weekly_sales'].shift(1)
        group['lag_2'] = group['weekly_sales'].shift(2)
        group['lag_3'] = group['weekly_sales'].shift(3)
        group['lag_4'] = group['weekly_sales'].shift(4)
        
        # Rolling stats on lagged data to prevent leakage of target
        group['rolling_mean_4'] = group['lag_1'].rolling(window=4).mean()
        group['rolling_std_4'] = group['lag_1'].rolling(window=4).std()
        
        feature_dfs.append(group)
        
    processed_df = pd.concat(feature_dfs, ignore_index=True)
    
    # Add date features
    processed_df['month'] = processed_df['date'].dt.month
    processed_df['week_of_year'] = processed_df['date'].dt.isocalendar().week.astype(int)
    
    # Drop rows with nulls caused by lags/rolling windows
    processed_df.dropna(inplace=True)
    
    # 3. Encoding product category (One-hot encoding)
    processed_df = pd.get_dummies(processed_df, columns=['category'], prefix='cat', dtype=int)
    
    # Define features and target
    # Get all dummy column names
    cat_dummy_cols = [col for col in processed_df.columns if col.startswith('cat_')]
    feature_cols = ['lag_1', 'lag_2', 'lag_3', 'lag_4', 'rolling_mean_4', 'rolling_std_4', 'month', 'week_of_year'] + cat_dummy_cols
    target_col = 'weekly_sales'
    
    # 4. Time-based Split: Train 2019-2022, Test 2023
    train_mask = processed_df['date'] < '2023-01-01'
    test_mask = processed_df['date'] >= '2023-01-01'
    
    train_df = processed_df[train_mask].copy()
    test_df = processed_df[test_mask].copy()
    
    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]
    
    logger.info(f"Training observations (2019-2022): {len(train_df)}")
    logger.info(f"Testing observations (2023): {len(test_df)}")
    
    # 5. Train Model
    model = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # 6. Predict and Evaluate
    predictions = model.predict(X_test)
    test_df['predicted_sales'] = predictions
    
    rmse = root_mean_squared_error(y_test, predictions)
    mape = mean_absolute_percentage_error(y_test, predictions)
    
    metrics = {
        'rmse': float(rmse),
        'mape': float(mape)
    }
    
    logger.info(f"Forecasting Model Trained. Validation Metrics: RMSE={rmse:.2f}, MAPE={mape:.2%}")
    return model, feature_cols, test_df, metrics
