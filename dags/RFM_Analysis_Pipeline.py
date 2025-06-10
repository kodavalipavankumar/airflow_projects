import os
import pandas as pd
from datetime import datetime, timedelta

from airflow.models import DAG

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from airflow.models import Variable
from airflow.utils.dates import days_ago

from airflow.providers.postgres.hooks.postgres import PostgresHook


def preprocess_and_insert(ti):
    df_online_retail = pd.read_csv('/data/Online_Retail.csv',encoding='ISO-8859-1')

    df_online_retail["InvoiceDate"] = pd.to_datetime(df_online_retail["InvoiceDate"], format="%m/%d/%Y %H:%M", errors="coerce")

    df_online_retail["CustomerID"] = pd.to_numeric(df_online_retail["CustomerID"], errors="coerce").astype("Int64")
    # df_online_retail["CustomerID"] = df_online_retail["CustomerID"].apply(lambda x: int(x) if pd.notna(x) else None)
    df_online_retail["Quantity"] = df_online_retail["Quantity"].apply(lambda x: int(x) if pd.notna(x) else 0)
    df_online_retail["UnitPrice"] = df_online_retail["UnitPrice"].apply(lambda x: float(x) if pd.notna(x) else 0.0)

    df_online_retail["Description"] = df_online_retail["Description"].fillna('')
    df_online_retail["Country"] = df_online_retail["Country"].fillna('')

    df_online_retail['InvoiceDay'] = df_online_retail['InvoiceDate'].dt.date
    
    pg_hook = PostgresHook(
        postgres_conn_id = 'postgres_localhost',
        schema='test'
    )

    data = [
        (
            str(row["InvoiceNo"]),
            str(row["StockCode"]),
            row["Description"],
            row["Quantity"],
            row["InvoiceDate"].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row["InvoiceDate"]) else None,
            row["UnitPrice"],
            row["CustomerID"] if pd.notna(row["CustomerID"]) else None,
            row["Country"],
            row["InvoiceDay"].strftime('%Y-%m-%d') if pd.notna(row["InvoiceDay"]) else None
        )
        for _, row in df_online_retail.iterrows()
    ]

    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.executemany(
        """
            insert into online_retail(InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country, InvoiceDay)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data
    )

    # for i, row in enumerate(data):
    #     try:
    #         cursor.execute(
    #             """
    #             INSERT INTO online_retail (
    #                 InvoiceNo, StockCode, Description, Quantity,
    #                 InvoiceDate, UnitPrice, CustomerID, Country, InvoiceDay
    #             )
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """,
    #             row
    #         )
    #     except Exception as e:
    #         print(f"Failed to insert row {i}: {row}")
    #         print(f"Error: {e}")
    #         conn.rollback()
    #         break

    conn.commit()
    cursor.close()
    conn.close()

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,12)}

with DAG(
    dag_id = 'data_insertion_rfm',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['rfm_pipeline']
) as dag:
    
    # 1. Create a table in DBeaver
    task_create_table = PostgresOperator(
        task_id = 'create_table',
        postgres_conn_id='postgres_localhost',
        sql = """
                CREATE TABLE if not exists online_retail (
                    InvoiceNo VARCHAR(20),
                    StockCode VARCHAR(20),
                    Description TEXT,
                    Quantity INTEGER,
                    InvoiceDate TIMESTAMP,
                    UnitPrice NUMERIC(10,2),
                    CustomerID BIGINT,
                    Country VARCHAR(255),
                    InvoiceDay TIMESTAMP
                );              
            """
    )

    # 2. Preprocess the data and insert into the table
    task_preprocess_insert = PythonOperator(
        task_id = 'preprocess_insert',
        python_callable = preprocess_and_insert,
        do_xcom_push = True
    )


