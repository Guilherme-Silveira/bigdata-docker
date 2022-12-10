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
        image='guisilveira/spark-base',
        container_name='spark-airflow-test',
        api_version='auto',
        auto_remove=False,
        command="echo hello",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
        )

  t1
