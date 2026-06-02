from datetime import datetime, timedelta
import os
import json
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowFailException

DATA_DIR = '/opt/airflow/data'
USERS_JSON = os.path.join(DATA_DIR, 'new_users.json')
POINTS_CSV = os.path.join(DATA_DIR, 'new_delivery_points.csv')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


def validate_and_load_users():
    if not os.path.exists(USERS_JSON) or os.path.getsize(USERS_JSON) == 0:
        print("Файл new_users.json пуст или отсутствует. Пропуск задачи.")
        return

    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError as e:
            raise AirflowFailException(f"Невалидный JSON-формат: {e}")

    valid_users = []
    for u in users:
        if u.get('name') and u.get('login') and u.get('password'):
            valid_users.append((u['name'], u['login'], u['password'], u.get('role_id', 2)))

    if valid_users:
        pg_hook = PostgresHook(postgres_conn_id='postgres_shop')
        insert_query = """
            INSERT INTO public.users (name, login, password, role_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (login) DO NOTHING;
        """
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        cursor.executemany(insert_query, valid_users)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Успешно обработано и добавлено пользователей: {len(valid_users)}")


def validate_and_load_delivery_points():
    if not os.path.exists(POINTS_CSV) or os.path.getsize(POINTS_CSV) == 0:
        print("Файл new_delivery_points.csv пуст или отсутствует. Пропуск задачи.")
        return

    try:
        df = pd.read_csv(POINTS_CSV, sep=',', encoding='utf-8')
    except Exception as e:
        raise AirflowFailException(f"Ошибка чтения CSV: {e}")

    df = df.dropna(subset=['method', 'address'])

    if not df.empty:
        pg_hook = PostgresHook(postgres_conn_id='postgres_shop')
        insert_query = """
            INSERT INTO public.delivery_point (method, address)
            VALUES (%s, %s)
            ON CONFLICT (method, address) DO NOTHING;
        """
        data_to_insert = list(df[['method', 'address']].itertuples(index=False, name=None))

        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Успешно обработано и добавлено пунктов выдачи: {len(data_to_insert)}")


with DAG(
        '1_etl_csv_json_to_postgres',
        default_args=default_args,
        description='Загрузка и валидация данных из JSON и CSV в PostgreSQL',
        schedule_interval='@daily',
        catchup=False
) as dag:
    load_users_task = PythonOperator(
        task_id='load_users_from_json',
        python_callable=validate_and_load_users
    )

    load_points_task = PythonOperator(
        task_id='load_delivery_points_from_csv',
        python_callable=validate_and_load_delivery_points
    )

    load_users_task >> load_points_task