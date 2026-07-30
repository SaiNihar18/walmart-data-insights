import pandas as pd
import pytest
from src.etl import transform_data

def test_transform_data_drops_duplicates():
    # Arrange: raw data with one duplicate row
    data = {
        'invoice_id': [1, 2, 2],
        'Branch': ['A', 'B', 'B'],
        'City': ['X', 'Y', 'Y'],
        'category': ['Food', 'Sports', 'Sports'],
        'unit_price': ['$10.00', '$20.00', '$20.00'],
        'quantity': [5.0, 10.0, 10.0],
        'date': ['01/01/2023', '02/01/2023', '02/01/2023'],
        'time': ['12:00', '13:00', '13:00'],
        'payment_method': ['Cash', 'Credit card', 'Credit card'],
        'rating': [8.5, 9.0, 9.0],
        'profit_margin': [0.15, 0.20, 0.20]
    }
    df = pd.DataFrame(data)
    
    # Act
    df_clean = transform_data(df)
    
    # Assert: duplicates dropped
    assert df_clean.shape[0] == 2
    assert 2 in df_clean['invoice_id'].values

def test_transform_data_drops_nulls():
    # Arrange: raw data with a row containing a null value
    data = {
        'invoice_id': [1, 2],
        'Branch': ['A', None],  # Null in branch
        'City': ['X', 'Y'],
        'category': ['Food', 'Sports'],
        'unit_price': ['$10.00', '$20.00'],
        'quantity': [5.0, 10.0],
        'date': ['01/01/2023', '02/01/2023'],
        'time': ['12:00', '13:00'],
        'payment_method': ['Cash', 'Credit card'],
        'rating': [8.5, 9.0],
        'profit_margin': [0.15, 0.20]
    }
    df = pd.DataFrame(data)
    
    # Act
    df_clean = transform_data(df)
    
    # Assert: null rows dropped
    assert df_clean.shape[0] == 1
    assert df_clean.iloc[0]['invoice_id'] == 1

def test_transform_data_parses_currency_and_calculates_total():
    # Arrange: raw data with currency symbol
    data = {
        'invoice_id': [1],
        'Branch': ['A'],
        'City': ['X'],
        'category': ['Food'],
        'unit_price': ['$12.50'],
        'quantity': [4.0],
        'date': ['01/01/2023'],
        'time': ['12:00'],
        'payment_method': ['Cash'],
        'rating': [8.5],
        'profit_margin': [0.15]
    }
    df = pd.DataFrame(data)
    
    # Act
    df_clean = transform_data(df)
    
    # Assert
    assert df_clean.iloc[0]['unit_price'] == 12.50
    assert df_clean.iloc[0]['total'] == 50.00
