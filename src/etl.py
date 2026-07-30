import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_data(file_path: str) -> pd.DataFrame:
    """
    Extracts data from the given CSV file path.
    """
    logger.info(f"Extracting data from {file_path}")
    try:
        df = pd.read_csv(file_path, encoding_errors='ignore')
        logger.info(f"Successfully extracted {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        raise

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw Walmart sales data:
    1. Removes duplicate entries.
    2. Drops rows with null values.
    3. Formats 'unit_price' by stripping '$' and converting to float.
    4. Calculates 'total' revenue.
    """
    logger.info("Starting data transformation.")
    df_clean = df.copy()
    
    # Remove duplicates
    initial_rows = df_clean.shape[0]
    df_clean.drop_duplicates(inplace=True)
    duplicates_removed = initial_rows - df_clean.shape[0]
    logger.info(f"Removed {duplicates_removed} duplicate rows.")
    
    # Handle missing values
    before_nulls = df_clean.shape[0]
    df_clean.dropna(inplace=True)
    nulls_removed = before_nulls - df_clean.shape[0]
    logger.info(f"Removed {nulls_removed} rows with missing values.")
    
    # Fix unit_price data type
    if 'unit_price' in df_clean.columns:
        if df_clean['unit_price'].dtype == 'object':
            df_clean['unit_price'] = (
                df_clean['unit_price']
                .astype(str)
                .str.replace('$', '', regex=False)
                .astype(float)
            )
            logger.info("Formatted 'unit_price' to float.")
            
    # Calculate total sales amount if quantity is available
    if 'unit_price' in df_clean.columns and 'quantity' in df_clean.columns:
        df_clean['total'] = df_clean['unit_price'] * df_clean['quantity']
        logger.info("Calculated 'total' amount column (unit_price * quantity).")
        
    logger.info(f"Transformation complete. Cleaned dataset has {df_clean.shape[0]} rows.")
    return df_clean

def load_data(df: pd.DataFrame, table_name: str, engine, if_exists: str = 'replace') -> None:
    """
    Loads a Pandas DataFrame into the specified database table using the provided SQLAlchemy engine.
    """
    logger.info(f"Loading data into table '{table_name}' using {if_exists} method.")
    try:
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        logger.info(f"Successfully loaded data into table '{table_name}'.")
    except Exception as e:
        logger.error(f"Failed to load data to database: {e}")
        raise
