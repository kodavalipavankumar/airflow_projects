from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# common parameters to intialise the operator in default mode

default_args = {
    'owner':'pavankumar',
    'retries':5,
    'retry_delay':timedelta(minutes=2)
}

with DAG(
    dag_id = 'our_first_dag_v2',
    default_args=default_args,
    description = 'This is our first dag that we write',
    start_date = datetime(2025,5,15,2), # starting at 2am in the morning from 18th may
    schedule_interval = '@daily'
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command = "echo hello world, this is the first task!"
    )

    task2 = BashOperator(
        task_id = 'second_task',
        bash_command = "echo hey, I am task2 and will be running after the execution of task1"
    )

    task3 = BashOperator(
        task_id = 'third_task',
        bash_command = "echo hey, I am task3 and will be running after task1 along with task2"
    )

    task1.set_downstream(task2)
    task1.set_downstream(task3)