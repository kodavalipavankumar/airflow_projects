from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def print_hello(s = 'airflow'):
    print(f"Hello World from {s}!")

default_args = {
    'start_date': datetime(2025, 5, 15),
}

with DAG(
    'hello_world',
    default_args=default_args,
    schedule_interval='@daily',  # run once a day
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id='task_1',
        python_callable=print_hello,
        op_kwargs={'s': 'kodavali'},
    )

    task2 = PythonOperator(
        task_id='task_2',
        python_callable=print_hello,
        op_kwargs={'s': 'pavan'},
    )

    task3 = PythonOperator(
        task_id='task_3',
        python_callable=print_hello,
        op_kwargs={'s': 'kumar'},
    )

    task1 >> [task2, task3]