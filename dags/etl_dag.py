import os
import pandas as pd
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,10)}

def process_datetime(ti):
    dt = ti.xcom_pull(task_ids='get_datetime')
    if not dt:
        raise Exception('No datetime value.')

    dt = str(dt).split()

    return {
        'year': int(dt[-1]),
        'month': dt[1],
        'day':int(dt[2]),
        'time': dt[3],
        'day_of_week': dt[0]
    }

def save_datetime(ti, **context):
    dt_processed = ti.xcom_pull(task_ids='process_datetime')

    if not dt_processed:
        raise Exception('No processed datetime')
    
    dag_run = context.get('dag_run')
    dag_status = dag_run.get_state() if dag_run else 'unkwon'
    
    dt_processed.update({
                        'dag_id':context['dag'].dag_id,
                        'dag_status':dag_status
                         })

    df = pd.DataFrame([dt_processed])
    csv_path = Variable.get('etl_pipeline_csv_path')
    if os.path.exists(csv_path):
        df_header = False
        df_mode = 'a'
    else:
        df_mode = 'w'
        df_header=True

    df.to_csv(csv_path, index=False, mode=df_mode, header=df_header)

with DAG(
    dag_id='etl_pipeline_dag',
    default_args = default_args,
    schedule_interval = '*/10 * * * *',
    catchup=False
) as dag: 
    # 1. Get current datetime
    task_get_datetime = BashOperator(
        task_id = 'get_datetime',
        bash_command = 'date',
        do_xcom_push=True
    )

    # 2. Process current datetime
    task_process_datetime = PythonOperator(
        task_id='process_datetime',
        python_callable=process_datetime
    )

    # 3. Save the current datetime
    task_save_datetime = PythonOperator(
        task_id='save_datetime',
        python_callable=save_datetime,
        provide_context = True
    )

    task_get_datetime >> task_process_datetime >> task_save_datetime