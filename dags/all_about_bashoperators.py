from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_arg = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,10)}

def save_to_temp(ti):
    files_list = ti.xcom_pull(task_ids='list_files')
    with open('//tmp//my_temp_file.txt','a') as f:
        f.write("\nList of DAGs:\n")
        f.write(files_list + "\n")


_dag = DAG(
    dag_id = 'bashoperator_dag',
    description = 'This dag has everything related to bash operator',
    default_args = default_arg,
    schedule_interval = '0 10 * * *',
    catchup = False
    )

hello_task = BashOperator(
    task_id = 'say_hello',
    bash_command = 'echo Hello, Welocme to Airflow BashOperator',
    dag = _dag
)

list_files = BashOperator(
    task_id = 'list_files',
    bash_command = 'ls -l //opt//airflow//dags',
    do_xcom_push = True,
    dag = _dag
)

create_temp_file = BashOperator(
    task_id='create_file',
    bash_command='echo "Hello from Airflow container" > //tmp//my_temp_file.txt',
    dag=_dag,
)

save_files_list = PythonOperator(
    task_id = 'save_files_list',
    python_callable = save_to_temp
)


hello_task >> list_files >> create_temp_file >> save_files_list

