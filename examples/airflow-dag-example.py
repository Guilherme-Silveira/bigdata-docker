from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.docker_operator import DockerOperator


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

  t1 = DockerOperator(
        task_id='spark-airflow-test',
        image='guisilveira/test-application-spark-docker',
        container_name='spark-airflow-test',
        api_version='auto',
        auto_remove=True,
        command="/opt/spark/bin/spark-submit /app/test-application.py",
        docker_url="tcp://docker-proxy:2375",
        network_mode="bigdata-docker_bigdata"
        )

  t1
