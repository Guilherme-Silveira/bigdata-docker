#!/bin/bash

docker build --tag guisilveira/dbt-trino \
  --target dbt-third-party \
  --build-arg dbt_third_party=dbt-trino \
  --build-arg dbt_core_ref=dbt-core@1.2.latest \
  .
