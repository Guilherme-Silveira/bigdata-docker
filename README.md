# bigdata-docker

Arquitetura do projeto:
![architecture-docker](https://user-images.githubusercontent.com/40548889/206875691-757ee5f3-c9af-40be-96f6-e1f385b00412.png)



---

Esse projeto tem como finalidade prover um ambiente big data/modern data stack usando um ambiente de containers com Docker.

Para instalar o ambiente big data execute o seguinte comando:

```
docker-compose up -d
```

Portas e credenciais para acessar os serviços:

```
Minio:         http://localhost:9000
Minio Console: http://localhost:9001
```
  - Username: silveira
  - Password: guilherme@123

```
Trino:         http://localhost:8080
```
  - Username: trino

```
Airflow:       http://localhost:8081
```
  - Username: airflow
  - Password: airflow

```
Superset:      http://localhost:8088
```
  - Username: admin
  - Password: admin

Serviços que não precisam de credenciais:

```
Kafka:         http://localhost:9092
Jupyter:       http://localhost:8888
Airbyte:       http://localhost:8000
```



---
# Tutoriais

No diretório `examples` desse repo, tem alguns exemplos de como utilizar esse ambiente e seus componentes:
- Os arquivos `delta-docker.py` e `iceberg-docker.py` mostram como precisa ser feita a criação da SparkSession de acordo com o formato de Lakehouse que será utilizado (Delta ou Iceberg). Esse ambiente suporta ambas tecnologias, então fique a vontade para escolher a que melhor te atenda.
- O arquivo `trino.sql` mostra a criação de algumas tabelas utilizando o Trino. O Trino já está configurado para criar tabelas no formato Delta e Iceberg.
- O arquivo `airflow-dag-example.py` mostra o exemplo de uma Dag criada para executar uma connection no Airbyte e depois executar um Job Spark/DBT. Como:
  - Nessa Dag, está sendo utilizado o DockerOperator, que permite que o Airflow crie um container Docker de acordo com as configurações passadas. Para que o Docker Operator funcione corretamente, é preciso que o container que executa o Airflow consiga acessar o `docker.sock`. Para isso, foi configurado um container adicional chamado `docker-proxy`, então em todas as Dags que precisem usar o Docker Operator, no parâmetro `docker_url`, sempre será passado por parâmetro o endpoint do container `docker-proxy`.
  - O Docker Operator é muito versátil, então no exemplo desse repo, foi chamado um job Spark e um DBT, simplesmente modificando a imagem passada como argumento no Operator, dando uma flexibilidade incrível para a Stack.

---
- Criando uma imagem com um Job Spark:
  - Acesse o diretório `examples/build-job-spark`. Dentro dele, crie o arquivo `.py` com seu job Spark. Para contruir a imagem, use como base a imagem `guisilveira/spark-base`. Ela contém todos os Jars necessários para trabalhar com Delta e Iceberg. Exemplo de Dockerfile:
    - ``` Dockerfile
        FROM guisilveira/spark-base

        USER root

        RUN mkdir -p /app

        COPY ./test-application.py /app/

        WORKDIR /app

        USER 1001
      ```
  - Build a imagem:
    - ``` 
        $ docker build -t guisilveira/test-application-spark .
        $ docker push guisilveira/test-application-spark 
      ```
- Criando uma imagem com um Job DBT:
  - Acesse o diretório `examples/build-job-dbt`. Para criar a imagem, siga os seguintes passos (nesse projeto tem uma imagem de exemplo, mas os steps serão os mesmos para qualquer outro projeto):

    - Crie a imagem base do DBT, utilizando o Adapter do Data Warehouse/Lakehouse que será utilizado. No nosso caso, será o Trino, então para criar a imagem, eu usei como base um Dockerfile fornecido pela própria DBT.
      ```
      $ cd dbt/build-dbt-trino
      $ docker build --tag guisilveira/dbt-trino \
        --target dbt-third-party \
        --build-arg dbt_third_party=dbt-trino \
        --build-arg dbt_core_ref=dbt-core@1.2.latest \
        .
      ```
    - Crie o seu projeto DBT. Eu usei o exemplo fornecido pela própria DBT, mas fique a vontade para criar o seu. Nesse caso, eu criei o mesmo projeto duas vezes, porém com uma pequena diferença, a tabela final em um deles será criada no formato Delta e a outra no formato Iceberg (esse ambiente suporta ambas tecnologias, então escolha a que mais sentido para o seu use case, nesse exemplo, vou mostrar os comandos simulando o uso do Iceberg)
      ```
      Instale o dbt-core na sua máquina local ou use uma imagem docker com um volume montado apontando para um diretório local e execute o seguinte comando

      $ dbt init jaffle_shop_iceberg
      ```

    - Modifique os arquivos dbt_project.yml e crie seus models no diretório models de acordo com seu use case (ou simplesmente use o exemplo que já está pronto)

    - Crie o arquivo profiles.yml (no nosso caso, profiles_iceberg.yml). Esse arquivo vai definir as configurações necessárias para conectar o DBT ao Trino
      ``` yml
      jaffle_shop:
        target: dev
        outputs:
          dev:
            type: trino
            user: trino
            host: trino
            port: 8080
            catalog: iceberg
            schema: transformed
            threads: 8
            http_scheme: http
            session_properties:
              query_max_run_time: 4h
              exchange_compression: True
      ```
    - Após essas etapas, crie a imagem Docker que será executada pelo Airflow, usando a nossa imagem do dbt-trino que foi criada anteriormente como base (Dockerfile-iceberg):
      ``` Dockerfile
      FROM guisilveira/dbt-trino

      COPY ./jaffle_shop_iceberg/ /usr/app/

      COPY ./profiles_iceberg.yml /root/.dbt/profiles.yml

      CMD [ "run" ]
      ```
      ```
      $ docker build -t guisilveira/dbt-jaffle-shop-iceberg -f ./Dockerfile-iceberg .
      $ docker push guisilveira/dbt-jaffle-shop-iceberg
      ```

OBS: eu estou utilizando o repo `guisilveira` nas minhas imagens Docker pois é meu repo pessoal, mas no ambiente de vocês, mude para o seu repo pessoal/enterprise.
