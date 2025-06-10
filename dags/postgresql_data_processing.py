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

def get_iris_data():
    sql = "select * from iris"
    pg_hook = PostgresHook(
        postgres_conn_id = 'postgres_localhost',
        schema='test'
    )
    pg_conn = pg_hook.get_conn()
    cursor = pg_conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
    
def process_iris_data(ti):
    iris = ti.xcom_pull(task_ids='get_iris_data')

    if not iris:
        raise Exception('No Data')
    
    df_iris = pd.DataFrame(
        data=iris,
        columns=['iris_id', 'iris_sepal_length', 'iris_sepal_width', 'iris_petal_length', 'iris_petal_width', 'iris_variety']
    )
    print(f"Shape of Iris before data processing: {df_iris.shape}")
    
    df_iris['sepal_area'] = df_iris['iris_sepal_length']*df_iris['iris_sepal_width']

    print(f"Shape of Iris after data processing: {df_iris.shape}")

    csv_path = Variable.get("tmp_iris_loc")
    if os.path.exists(csv_path):
        df_iris.to_csv(csv_path, index=False, mode='a',header=False)
    else:
        df_iris.to_csv(csv_path, index=False, mode='w',header=True)

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,12)
               }

with DAG(
    dag_id = 'data_processing',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['etl_pipeline']
) as dag:
    
    # 1. Get the Iris data from a table in Postgres
    task_get_iris_data = PythonOperator(
        task_id  = 'get_iris_data',
        python_callable = get_iris_data,
        do_xcom_push = True
    )

    # 2. Process the iris data 
    task_process_iris_data = PythonOperator(
        task_id = 'process_iris_data',
        python_callable = process_iris_data,
        do_xcom_push = True
    )

    # 3. Delete the 

    task_get_iris_data >> task_process_iris_data