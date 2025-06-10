from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner':'pavankumar',
    'retries':5,
    'retry_delay':timedelta(minutes=2)
}

def greet(ti):
    first_name = ti.xcom_pull(task_ids = 'get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids = 'get_name', key='last_name')
    age = ti.xcom_pull(task_ids = 'get_age', key='age')
    print(f"Hello world! I am {first_name} {last_name}, I'm {age} years old.")

def get_name(ti):
    ti.xcom_push(key='first_name', value='Pavan Kumar')
    ti.xcom_push(key='last_name', value='Kodavali')

def get_age(ti):
    ti.xcom_push(key='age',value='19')

with DAG(
    dag_id = 'python_operator',
    default_args = default_args,
    description='DAG to explore python operator',
    start_date = datetime(2025,5,17,2),
    schedule_interval = '@daily'

) as dag:
    task1 = PythonOperator(
        task_id = 'greet',
        python_callable = greet
        # ,op_kwargs = {'age':27}
    )

    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable = get_name
    )

    task3 = PythonOperator(
        task_id = 'get_age',
        python_callable = get_age
    )

    [task2, task3] >> task1