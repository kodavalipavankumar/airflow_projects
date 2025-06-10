from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def test_task():
    import pandas as pd
    print("✅ Airflow DAG ran successfully inside Docker! After updating")

default_args = {
    'start_date': datetime(2025, 5, 31),
    'catchup': False
}

with DAG(
    dag_id='test_docker_dag',
    default_args=default_args,
    schedule_interval= '@daily',  # Manual trigger
    tags=['test']
) as dag:

    run_test = PythonOperator(
        task_id='run_test_task',
        python_callable=test_task
    )
