import pandas as pd
from airflow.models import DAG
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

from operator_code.postgre_operators import PostgresDataFetcher
from operator_code.transformations import CustomTransformations
from operator_code.s3_operators import S3DataUploader

from airflow.operators.python import PythonOperator

def extract_transform(**kwargs):
    fetch = PostgresDataFetcher(conn_id='postgres_localhost')
    df = fetch.fetch_data(table = 'iris',limit=100)
    df.to_csv("//tmp/iris_100.csv")
    print(df.head())

def upload_to_s3():
    local_path = "//tmp/iris_100.csv"
    bucket_name = 'infodat-airflow-testing'
    s3_key = 'transformed/iris_100.csv'
    df = pd.read_csv(local_path)

    uploader = S3DataUploader(aws_conn_id='s3_conn')
    uploader.upload_dataframe(df = df, bucket_name=bucket_name, key=s3_key, file_format='csv',index=False)

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,12)}

with DAG(
    dag_id = 'postgre_to_s3',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['Data_Transfer']
) as dag: 
    
    task_pull_transform_data_postgre = PythonOperator(
        task_id = 'pull_transform_data_postgre',
        python_callable = extract_transform
    )

    task_upload_to_s3 = PythonOperator(
        task_id = 'Upload_to_s3',
        python_callable = upload_to_s3
    )

    task_pull_transform_data_postgre >> task_upload_to_s3