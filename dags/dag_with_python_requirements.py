from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from airflow.utils.dates import days_ago

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,10)}


def get_sklearn():
    import sklearn as sk
    print(f"SK-Learn Version is:{sk.__version__}")

def get_matplotlib():
    import matplotlib
    print(f"matplotlib with version: {matplotlib.__version__}")

with DAG(
    dag_id = 'dag_with_python_requirements',
    default_args=default_args,
    description='Dag to test the python requiremetns',
    schedule_interval = '0 0 * * *',
    catchup = False
) as dag:
    
    task1 = PythonOperator(
        task_id = 'get_sklearn',
        python_callable = get_sklearn
    )

    task2 = PythonOperator(
        task_id='get_matplotlib',
        python_callable=get_matplotlib
    )

    task1 >> task2