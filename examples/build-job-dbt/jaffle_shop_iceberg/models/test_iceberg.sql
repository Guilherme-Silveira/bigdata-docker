{{
  config(
    materialized = "incremental",
    properties={
        "format": "'PARQUET'",
        "location": "'s3a://transformed/test_iceberg'"
    }
  )
}}

with customers as (

    select
        id as customer_id,
        first_name,
        last_name

    from {{ var("hive_catalog") }}.{{ var("hive_schema") }}.customers

),

orders as (

    select
        id as order_id,
        user_id as customer_id,
        order_date,
        status

    from {{ var("hive_catalog") }}.{{ var("hive_schema") }}.orders

),

customer_orders as (

    select
        customer_id,

        min(order_date) as first_order_date,
        max(order_date) as most_recent_order_date,
        count(order_id) as number_of_orders

    from orders

    group by 1

),

final as (

    select
        customer_id,
        customers.first_name,
        customers.last_name,
        customer_orders.first_order_date,
        customer_orders.most_recent_order_date,
        coalesce(customer_orders.number_of_orders, 0) as number_of_orders

    from customers

    left join customer_orders using (customer_id) where number_of_orders != 0

)

select * from final