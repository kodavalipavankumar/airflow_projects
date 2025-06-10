# Importing necessary packages
import os
import pandas as pd
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from airflow.models import Variable
from airflow.utils.dates import days_ago

default_args = {'owner':'Pavan Kumar Kodavali',
               'retries':3,
               'retry_delay':timedelta(minutes=5),
               'start_date':days_ago(1),
               'end_date':datetime(2025,6,12)}

with DAG(
    dag_id = 'data_insertion',
    schedule_interval = '0 0 * * *',
    default_args = default_args,
    catchup = False,
    tags=['etl_pipeline']
) as dag:
    
    # Create a table in DBeaver
    task_create_table = PostgresOperator(
        task_id = 'create_table',
        postgres_conn_id='postgres_localhost',
        sql = """
                create table if not exists iris(
                iris_id real primary key,
                iris_sepal_length real,
                iris_sepal_width real,
                iris_petal_length real,
                iris_petal_width real,
                iris_variety character varying
                );
              """
    )

    # Insert data into table
    task_insert_table = PostgresOperator(
        task_id = 'insert_into_table',
        postgres_conn_id='postgres_localhost',
        sql = """
                create temp table iris_staging(
                iris_id real primary key,
                iris_sepal_length real,
                iris_sepal_width real,
                iris_petal_length real,
                iris_petal_width real,
                iris_variety character varying                
                );

                copy iris_staging(iris_id, iris_sepal_length, iris_sepal_width, iris_petal_length, iris_petal_width, iris_variety)
                from '/data/iris.csv'
                delimiter ','
                csv header;

                insert into iris(iris_id, iris_sepal_length, iris_sepal_width, iris_petal_length, iris_petal_width, iris_variety)
                select *
                from iris_staging s
                where not exists(
                    select 1 from iris i where i.iris_id = s.iris_id
                );
            """
    )

    task_create_table >> task_insert_table