import os
import pandas as pd
import logging
import joblib
from src.modeling import segment_branches, forecast_weekly_sales

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    cleaned_csv = 'walmart_cleaned.csv'
    models_dir = 'models'
    
    if not os.path.exists(cleaned_csv):
        logger.error(f"Cleaned dataset '{cleaned_csv}' not found! Please run 'python run_etl.py' first.")
        return
        
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Load dataset
    df = pd.read_csv(cleaned_csv)
    
    # 1. Execute Branch Clustering
    logger.info("Executing K-Means Branch Clustering...")
    kmeans_model, scaler, clustered_df = segment_branches(df, n_clusters=4)
    
    # Save clustering artifacts
    joblib.dump(kmeans_model, os.path.join(models_dir, 'branch_kmeans.joblib'))
    joblib.dump(scaler, os.path.join(models_dir, 'branch_scaler.joblib'))
    clustered_df.to_csv('walmart_clustered_branches.csv', index=False)
    logger.info("Saved clustering models and 'walmart_clustered_branches.csv'.")
    
    # 2. Execute Weekly Sales Forecasting
    logger.info("Executing Weekly Sales Forecasting Model...")
    forecaster_model, feature_cols, test_eval_df, metrics = forecast_weekly_sales(df)
    
    # Save forecasting artifacts
    joblib.dump(forecaster_model, os.path.join(models_dir, 'sales_forecaster.joblib'))
    joblib.dump(feature_cols, os.path.join(models_dir, 'sales_features.joblib'))
    test_eval_df.to_csv('walmart_forecast_eval.csv', index=False)
    logger.info("Saved forecasting models and 'walmart_forecast_eval.csv'.")
    
    print("\n" + "="*50)
    print("MODELING STAGE COMPLETED SUCCESSFULLY")
    print("="*50)
    print(f"K-Means Clusters: 4 clusters fitted across 100 branches.")
    print(f"Sales Forecaster (XGBoost):")
    print(f"  Root Mean Squared Error (RMSE): ${metrics['rmse']:.2f}")
    print(f"  Mean Absolute Percentage Error (MAPE): {metrics['mape']:.2%}")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
