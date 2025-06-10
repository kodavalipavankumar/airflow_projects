import json
import time
import requests
from datetime import datetime, timedelta

from airflow.models import DAG

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from airflow.utils.dates import days_ago

def get(url: str) -> None:
    endpoint = url.split('/')[-1]
    _now = datetime.now()
    _now = f"{_now.year}_{_now.month}_{_now.day}_{_now.hour}_{_now.minute}_{_now.second}"
    res = requests.get(url)
    res = res.json()

    with open(f"//tmp//{endpoint}_{_now}.json", 'w') as f:
        json.dump(res,f)

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':0,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,15)}

with DAG(
    dag_id = 'parallel_dag',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['airflow_parallelism']
) as dag: 
    
    task_get_users = PythonOperator(
        task_id = 'get_users',
        python_callable = get,
        op_kwargs = {'url':'https://gorest.co.in/public/v2/users'}
    )

    task_get_posts = PythonOperator(
        task_id = 'get_posts',
        python_callable = get,
        op_kwargs = {'url':'https://gorest.co.in/public/v2/posts'}
    )

    task_get_comments = PythonOperator(
        task_id = 'get_comments',
        python_callable = get,
        op_kwargs = {'url':'https://gorest.co.in/public/v2/comments'}
    )

    task_get_todos = PythonOperator(
        task_id = 'get_todos',
        python_callable = get,
        op_kwargs = {'url':'https://gorest.co.in/public/v2/todos'}
    )

    task_get_users 
    task_get_posts 
    task_get_comments 
    task_get_todos
