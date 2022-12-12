from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator


default_args = {
  'owner': 'Guilherme da Silveira Souto Souza',
  'depends_on_post': False,
  'email': ['guilhermesilveira.s@hotmail.com'],
  'email_on_failure': False,
  'email_on_retry': False,
  'retries': 1,
  'retry_delay': timedelta(minutes=5)
}

with DAG(
    'test-spark-pipeline',
    default_args=default_args,
    start_date=datetime.now(),
    schedule_interval='@weekly',
    tags=['test', 'development', 'bash']
  ) as dag:

  t1 = AirbyteTriggerSyncOperator(
    task_id='test_airbyte',
    airbyte_conn_id='airbyte',
    connection_id='0c5af1ab-e900-4fdb-9708-8c7bec4d459e',
    asynchronous=False,
    timeout=7200,
    wait_seconds=3
  )
  # Job Spark
  t2 = DockerOperator(
    task_id='spark-airflow-test',
    image='guisilveira/test-application-spark-docker',
    container_name='spark-airflow-test',
    api_version='auto',
    auto_remove=True,
    command="/opt/spark/bin/spark-submit /app/test-application.py",
    docker_url="tcp://docker-proxy:2375",
    network_mode="bigdata-docker_bigdata"
  )
  # Job DBT
  t3 = DockerOperator(
    task_id='dbt-airflow-test',
    image='guisilveira/dbt-jaffle-shop-iceberg',
    container_name='dbt-airflow-test',
    api_version='auto',
    auto_remove=True,
    docker_url="tcp://docker-proxy:2375",
    network_mode="bigdata-docker_bigdata"
  )

  t1 >> t2 >> t3
