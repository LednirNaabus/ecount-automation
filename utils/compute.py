import pandas as pd

# Load to BQ (no stock_in and stock_out yet)
# Read the table
# Extract as df
# Perform calculation
# Load to a new table in BQ
# Query to verify if it worked
def compute_stock(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute

    Parameters:
        df (pd.DataFrame): Pandas dataframe needed to compute `stock_in` and `stock_out`.

    Returns:
        df (pd.DataFrame): New dataframe with the computed stock for each product.
    """
    df.sort_values(by='date')
    df['prev_balance'] = df.groupby('item_code')['balance'].shift(1)
    df[['stock_in', 'stock_out']] = df.apply(lambda row: 
        pd.Series({
            'stock_in': row['balance'],
            'stock_out': 0
        }) if pd.isna(row['prev_balance']) else (
            pd.Series({
                'stock_in': row['balance'] - row['prev_balance'],
                'stock_out': 0
            }) if row['balance'] > row['prev_balance'] else (
                pd.Series({
                    'stock_in': 0,
                    'stock_out': row['prev_balance'] - row['balance']
                }) if row['balance'] < row['prev_balance'] else
                pd.Series({
                    'stock_in': 0,
                    'stock_out': 0
                })
            )
        ), axis=1)

    return df