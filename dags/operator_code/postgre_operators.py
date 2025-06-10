import pandas as pd
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

class PostgresDataFetcher:

    def __init__(self,conn_id: str):
        self.conn_id = conn_id

    def fetch_data(self, table: str = None, limit: int = None, filters: dict = None, transformations: list = None):
        pg_hook = PostgresHook(
            postgres_conn_id = self.conn_id,
            schema='test'
        )

        if not table:
            raise Exception("Please enter the Table Name")
        
        sql = f"select * from {table}"

        if limit:
            sql += f" limit {limit}"

        df = pg_hook.get_pandas_df(sql=sql)

        return df
    
class PostgresDataUploader:

    def __init__(self, conn_id: str):
        self.conn_id = conn_id
    
    def upload_data(self, table: str):
        
