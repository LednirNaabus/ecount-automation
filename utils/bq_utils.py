from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.cloud.bigquery import SchemaField
from typing import List
import pandas as pd

from config import config
from utils.logger import EcountLogger

def get_client():
    """
    Returns a dictionary containing BigQuery client configuration details.

    Retrieves the BigQuery client, credentials, and project ID.

    Returns:
        dict: A dictionary with the BigQuery configuration details.
            - 'client': BigQuery client.
            - 'credentials': BigQuery credentials for authorization.
            - 'project_id': The GCP project ID associated with the credentials.
    """
    return {
        'client' : config.BQ_CLIENT,
        'credentials' : config.creds,
        'project_id' : config.creds.project_id
    }

def ensure_dataset(logger: EcountLogger, project_id: str, dataset_name: str, client: bigquery.Client):
    """
    Checks whether or not the dataset exists in your project.

    Parameters:
        logger (EcountLogger): Custom Ecount logger.
        project_id (str): The project ID associated with the credentials.
        dataset_name (str): The dataset name in your project.
        client (bigquery.Client): BigQuery client.
    """
    dataset_id = f"{project_id}.{dataset_name}"
    try:
        client.get_dataset(dataset_id)
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, timeout=30)
        logger.info(f"Created dataset '{dataset_id}'")

def ensure_table(logger: EcountLogger, project_id: str, dataset_name: str, table_name: str, client: bigquery.Client, schema=None):
    """
    Checks if the table exists. If the table exists, the data is appended to the existing table, otherwise, it creates the table and adds the data.

    Parameters:
        logger (EcountLogger): Custom Ecount logger.
        project_id (str): The project ID associated with the credentials.
        dataset_name (str): The dataset name in your project.
        table_name (str): The table name in the dataset.
        client (bigquery.Client): BigQuery client.
        schema (List[SchemaField], optional): Default is None; The BigQuery table schema.
    """
    table_id = f"{project_id}.{dataset_name}.{table_name}"
    try:
        client.get_table(table_id)
        logger.debug(f"Table {table_id} already exists.")
    except NotFound:
        table = bigquery.Table(table_id, schema=schema) if schema else bigquery.Table(table_id)
        client.create_table(table)
        logger.info(f"Created table '{table_id}'")

def generate_schema(df: pd.DataFrame) -> List[SchemaField]:
    """
    Helper function for generating schema in BigQuery tables.

    Parameters:
        df (pd.DataFrame): Pandas dataframe object that will be checked.

    Returns:
        schema (List[SchemaField]): The generated schema.
    """
    TYPE_MAPPING = {
        "i": "INTEGER",
        "u": "NUMERIC",
        "b": "BOOLEAN",
        "f": "FLOAT",
        "O": "STRING",
        "S": "STRING",
        "U": "STRING",
        "M": "TIMESTAMP",
    }
    
    schema = []
    for column, dtype in df.dtypes.items():
        val = df[column].iloc[0]
        mode = "REPEATED" if isinstance(val, list) else "NULLABLE"

        if isinstance(val, dict) or (mode == "REPEATED" and isinstance(val[0], dict)):
            fields = generate_schema(pd.json_normalize(val))
        else:
            fields = ()
        
        type = "RECORD" if fields else TYPE_MAPPING.get(dtype.kind)
        schema.append(
            SchemaField(
                name=column,
                field_type=type,
                mode=mode,
                fields=fields,
            )
        )

    return schema

def load_data_to_bq(logger: EcountLogger, df: pd.DataFrame , project_id: str, dataset_name: str, table_name: str, write_mode: str ="WRITE_APPEND", schema=None):
    """
    Loads a pandas DataFrame into a specified BigQuery table.

    Ensures that the target dataset and table exist before attempting to upload.
    Supports custom schemas and write modes (e.g., append or overwrite).
    Logs the outcome using the provided logger.

    Parameters:
        logger (EcountLogger): Custom Ecount logger.
        df (pd.DataFrame): Pandas dataframe that will be loaded to BigQuery table.
        project_id (str): The project ID associated with the credentials.
        dataset_name (str): The dataset name in your project.
        table_name (str): The table name in the dataset.
        write_mode (str): BigQuery write disposition. Default is `WRITE_APPEND`.
        schema (List[SchemaField], optional): Default is None; The BigQuery table schema.

    Returns:
        str: A message indicating whether the data upload was successful or failed.
    """
    client = get_client()['client']
    ensure_dataset(logger, project_id, dataset_name, client)
    ensure_table(logger, project_id, dataset_name, table_name, client, schema)
    table_id = f"{project_id}.{dataset_name}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=write_mode,
        autodetect=schema is None,
    )

    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        logger.info(f"Successfully loaded {df.shape[0]} rows into {table_id}")
        return f"Loaded {df.shape[0]} rows into {table_id}"
    except Exception as e:
        logger.error(f"Error uploading data to BigQuery: {e}")
        return f"Failed to upload data: {e}"