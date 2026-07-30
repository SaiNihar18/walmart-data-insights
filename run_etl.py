import os
import sys
import logging
from src.db import get_db_engine
from src.etl import extract_data, transform_data, load_data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    raw_csv_path = 'Walmart.csv'
    cleaned_csv_path = 'walmart_cleaned.csv'
    table_name = 'walmart'
    
    if not os.path.exists(raw_csv_path):
        logger.error(f"Raw data file '{raw_csv_path}' not found! Please download the dataset first.")
        sys.exit(1)
        
    try:
        # 1. Extract
        df_raw = extract_data(raw_csv_path)
        
        # 2. Transform
        df_clean = transform_data(df_raw)
        
        # Save cleaned file locally
        df_clean.to_csv(cleaned_csv_path, index=False)
        logger.info(f"Saved cleaned data locally to '{cleaned_csv_path}'.")
        
        # 3. Load into Database
        logger.info("Attempting to load data to the database...")
        try:
            engine = get_db_engine()
            load_data(df_clean, table_name, engine, if_exists='replace')
            logger.info("ETL Pipeline completed successfully with database load.")
        except Exception as db_err:
            logger.warning(
                f"Database load failed: {db_err}\n"
                "Ensure your database is running (e.g., via Docker Compose) and credentials in .env are correct.\n"
                f"Note: Cleaned data was successfully saved to '{cleaned_csv_path}'."
            )
            
    except Exception as e:
        logger.error(f"ETL pipeline run failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
