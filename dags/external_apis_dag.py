import os
from datetime import datetime, timedelta
import json

from airflow.models import DAG

from airflow.operators.python import PythonOperator

from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator

from airflow.utils.dates import days_ago

# go to airflow admin-->connections (create a http connection)

def save_posts(ti) -> None:
    posts = ti.xcom_pull(task_ids = 'get_posts')

    with open('//tmp//posts.json','w') as f:
        json.dump(posts,f)


default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,12)}

with DAG(
    dag_id = 'api_dag',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['external_apis']
) as dag:
    
    task_is_api_active = HttpSensor(
        task_id = 'is_api_active',
        http_conn_id = 'api_posts',
        endpoint = 'posts/'
    )

    task_get_posts = SimpleHttpOperator(
        task_id = 'get_posts',
        http_conn_id = 'api_posts',
        endpoint = 'posts/',
        method = 'GET',
        response_filter = lambda response: json.loads(response.text),
        log_response=True
    )

    task_save_posts = PythonOperator(
        task_id = 'save_posts',
        python_callable = save_posts
    )

    task_is_api_active >> task_get_posts >> task_save_posts