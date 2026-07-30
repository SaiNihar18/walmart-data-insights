import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_engine():
    """
    Creates and returns a SQLAlchemy engine based on environment variables.
    Supports both 'postgresql' and 'mysql'.
    """
    db_type = os.getenv('DB_TYPE', 'postgresql').lower()
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'walmart_db')
    
    # URL encode the password to handle special characters (e.g. @, :, /)
    safe_password = urllib.parse.quote_plus(password)
    
    if db_type == 'postgresql':
        connection_uri = f"postgresql+psycopg2://{user}:{safe_password}@{host}:{port}/{db_name}"
    elif db_type == 'mysql':
        connection_uri = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{db_name}"
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}. Use 'postgresql' or 'mysql'.")
        
    return create_engine(connection_uri)
