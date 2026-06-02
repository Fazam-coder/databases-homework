from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


def get_ch_client():
    import clickhouse_connect
    return clickhouse_connect.get_client(host='clickhouse_node', port=8123, username='default', password='clickhouse_pass')


def create_clickhouse_schema():
    client = get_ch_client()

    client.command("""
        CREATE TABLE IF NOT EXISTS default.ch_orders (
            id Int64,
            user_id Nullable(Int64),
            created_at DateTime,
            status String,
            price Nullable(Int64)
        ) ENGINE = ReplacingMergeTree()
        ORDER BY id;
    """)

    client.command("""
        CREATE TABLE IF NOT EXISTS default.ch_order_elements (
            id Int64,
            order_id Int64,
            product_name String,
            color String,
            quantity Int32,
            unit_price Int32,
            discount Int32,
            created_at DateTime
        ) ENGINE = ReplacingMergeTree()
        ORDER BY (order_id, id);
    """)

    client.command("""
        CREATE TABLE IF NOT EXISTS default.mart_sales_performance (
            dt Date,
            total_revenue Float64,
            orders_count UInt64,
            avg_order_value Float64,
            total_items_sold UInt64,
            updated_at DateTime
        ) ENGINE = MergeTree()
        ORDER BY dt;
    """)


def sync_postgres_to_clickhouse(**context):
    import pandas as pd

    pg_hook = PostgresHook(postgres_conn_id='postgres_shop')
    ch_client = get_ch_client()

    orders_df = pg_hook.get_pandas_df("SELECT id, user_id, created_at, status, price FROM public.orders")
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at']).dt.tz_localize(None)

    orders_df = orders_df.where(pd.notnull(orders_df), None)
    orders_data = orders_df.values.tolist()

    if orders_data:
        ch_client.insert('default.ch_orders', orders_data,
                         column_names=['id', 'user_id', 'created_at', 'status', 'price'])

    query_elements = """
        SELECT 
            oe.id, oe.order_id, p.name as product_name, pe.color, 
            oe.quantity, oe.unit_price, oe.discount, o.created_at
        FROM public.orderelem oe
        JOIN public.orders o ON oe.order_id = o.id
        JOIN public.product_element pe ON oe.elem_id = pe.id
        JOIN public.product p ON pe.product_id = p.id
    """
    elem_df = pg_hook.get_pandas_df(query_elements)
    elem_df['created_at'] = pd.to_datetime(elem_df['created_at']).dt.tz_localize(None)

    elem_df = elem_df.where(pd.notnull(elem_df), None)
    elem_data = elem_df.values.tolist()

    if elem_data:
        ch_client.insert('default.ch_order_elements', elem_data,
                         column_names=['id', 'order_id', 'product_name', 'color', 'quantity', 'unit_price', 'discount',
                                       'created_at'])

    print("Данные успешно синхронизированы в ClickHouse.")


def build_analytical_mart():
    ch_client = get_ch_client()
    ch_client.command("TRUNCATE TABLE default.mart_sales_performance")

    mart_query = """
        INSERT INTO default.mart_sales_performance (dt, total_revenue, orders_count, avg_order_value, total_items_sold, updated_at)
        SELECT 
            toDate(created_at) as dt,
            sum(quantity * unit_price) as total_revenue,
            uniq(order_id) as orders_count,
            if(orders_count > 0, total_revenue / orders_count, 0) as avg_order_value,
            sum(quantity) as total_items_sold,
            now() as updated_at
        FROM default.ch_order_elements
        GROUP BY dt
        ORDER BY dt
    """
    ch_client.command(mart_query)
    print("Аналитическая витрина mart_sales_performance успешно обновлена.")
    print(ch_client.query_df("SELECT * FROM default.mart_sales_performance LIMIT 10"))


with DAG(
        '2_analytics_postgres_to_clickhouse',
        default_args=default_args,
        description='Репликация данных в ClickHouse и построение аналитической витрины',
        schedule_interval='@daily',
        catchup=False
) as dag:
    init_schema = PythonOperator(
        task_id='create_clickhouse_tables',
        python_callable=create_clickhouse_schema
    )

    sync_data = PythonOperator(
        task_id='sync_postgres_to_clickhouse',
        python_callable=sync_postgres_to_clickhouse
    )

    build_mart = PythonOperator(
        task_id='build_sales_data_mart',
        python_callable=build_analytical_mart
    )

    init_schema >> sync_data >> build_mart