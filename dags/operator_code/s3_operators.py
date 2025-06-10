import pandas as pd
from io import StringIO
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

class S3DataUploader:
    def __init__(self, aws_conn_id: str):
        self.aws_conn_id = aws_conn_id

    def upload_dataframe(self, df: pd.DataFrame, bucket_name: str, key: str, file_format: str = 'csv', index: bool = False):
        hook = S3Hook(aws_conn_id=self.aws_conn_id)
        buffer = StringIO()

        if file_format == 'csv':
            df.to_csv(buffer, index=index)
            content_type = 'text/csv'
        elif file_format == 'json':
            df.to_json(buffer, orient='records', lines=True)
            content_type = 'application/json'
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        hook.load_string(string_data=buffer.getvalue(), key=key, bucket_name=bucket_name, replace=True, encrypt=False)
