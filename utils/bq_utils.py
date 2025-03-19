from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.exceptions import NotFound
import json
import os
import logging
import pandas as pd

from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_client():
    return {
        'client' : config.BQ_CLIENT,
        'credentials' : config.creds,
        'project_id' : config.creds.project_id
    }

def ensure_dataset(project_id: str, dataset_name: str, client: bigquery.Client):
    dataset_id = f"{project_id}.{dataset_name}"
    try:
        client.get_dataset(dataset_id)
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, timeout=30)
        logging.info(f"Created dataset '{dataset_id}'")

def ensure_table(project_id: str, dataset_name: str, table_name: str, client: bigquery.Client, schema=None):
    table_id = f"{project_id}.{dataset_name}.{table_name}"
    try:
        client.get_table(table_id)
        print(f"Table {table_id} already exists.")
    except NotFound:
        table = bigquery.Table(table_id, schema=schema) if schema else bigquery.Table(table_id)
        client.create_table(table)
        logging.info(f"Created table '{table_id}'")

def load_data_to_bq(df: pd.DataFrame , project_id: str, dataset_name: str, table_name: str, write_mode="WRITE_APPEND", schema=None):
    client = get_client()['client']
    ensure_dataset(project_id, dataset_name, client)
    ensure_table(project_id, dataset_name, table_name, client, schema)
    table_id = f"{project_id}.{dataset_name}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=write_mode,
        autodetect=schema is None,
    )

    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        logging.info(f"Successfully loaded {df.shape[0]} rows into {table_id}")
        return f"Loaded {df.shape[0]} rows into {table_id}"
    except Exception as e:
        print(f"Error uploading data to BigQuery: {e}", exc_info=True)
        return f"Failed to upload data: {e}"