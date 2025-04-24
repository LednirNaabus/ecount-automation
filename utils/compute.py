import pandas as pd

# Load to BQ (no stock_in and stock_out yet)
# Read the table
# Extract as df
# Perform calculation
# Load to a new table in BQ
# Query to verify if it worked
def compute_stock(row):
    """
    Computes the `stock_in` and `stock_out` for each product.

    Parameters:
        row (Any): The row to apply stock computation.
    """
    if pd.isna(row['prev_balance']):
        return pd.Series({
            'stock_in': row['balance'],
            'stock_out': 0
        })
    elif row['balance'] > row['prev_balance']:
        return pd.Series({
            'stock_in': row['balance'] - row['prev_balance'],
            'stock_out': 0
        })
    elif row['balance'] < row['prev_balance']:
        return pd.Series({
            'stock_in': 0,
            'stock_out': row['prev_balance'] - row['balance']
        })
    else:
        return pd.Series({
            'stock_in': 0,
            'stock_out': 0
        })

def apply_computation_stock(df: pd.DataFrame) -> pd.DataFrame:
    """
    First sorts the values in the data frame by date. Then shifts the row by 1, to create `prev_balance`. Finally, adds `stock_in` and `stock_out` column by applying `compute_stock()` to each row. 

    Parameters:
        df (pd.DataFrame): Pandas data frame needed to compute `stock_in` and `stock_out`.

    Returns:
        df (pd.DataFrame): New data frame with the computed stock for each product.
    """
    df.sort_values(by='date')
    df['prev_balance'] = df.groupby('item_code')['balance'].shift(1)
    df[['stock_in', 'stock_out']] = df.apply(compute_stock, axis=1)
    return df