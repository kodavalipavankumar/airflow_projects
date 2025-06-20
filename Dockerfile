FROM apache/airflow:2.8.1
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt
RUN pip install apache-airflow-providers-http
RUN pip install apache-airflow-providers-amazon