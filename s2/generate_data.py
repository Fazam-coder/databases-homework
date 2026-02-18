import random
import hashlib
import json
from datetime import datetime, timedelta
from typing import List

TABLES_CONFIG = {
    'orders': 300_000,
    'orderelem': 320_000,
    'audit_log': 280_000,
    'product_element': 250_000,
}

# Существующие ID из базы (по changelog-COMPLETE.xml)
EXISTING_USERS = [1, 2, 3, 4, 5, 6]
EXISTING_PRODUCTS = [1, 2, 3]
EXISTING_DELIVERY_POINTS = [1, 2, 3]
ORDER_STATUSES = ['new', 'processing', 'paid', 'shipped', 'delivered', 'cancelled']
AUDIT_ACTIONS = ['BEFORE_INSERT', 'AFTER_INSERT', 'BEFORE_UPDATE', 'AFTER_UPDATE',
                 'BEFORE_DELETE', 'AFTER_DELETE']


def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def generate_ip() -> str:
    return f"{random.randint(1, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"


def generate_timestamp(days_back: int = 365) -> str:
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return (datetime.now() - delta).strftime('%Y-%m-%d %H:%M:%S')


def generate_jsonb(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False).replace("'", "''")


def generate_tsrange() -> str:
    start = generate_timestamp(30)
    end_delta = random.randint(1, 48)
    end = datetime.strptime(start, '%Y-%m-%d %H:%M:%S') + timedelta(hours=end_delta)
    return f"tsrange('{start}', '{end.strftime('%Y-%m-%d %H:%M:%S')}', '[)')"


def generate_orders(count: int) -> List[str]:
    rows = []
    status_weights = [0.15, 0.25, 0.20, 0.15, 0.20, 0.05]

    start_id = 9

    for i in range(count):
        order_id = start_id + i

        # Skewed: 70% заказов от 2 пользователей (из 6)
        if random.random() < 0.70:
            user_id = random.choice([1, 2])
        else:
            user_id = random.randint(1, 10000)

        user_id_val = 'NULL' if random.random() < 0.15 else str(user_id)
        created_at = generate_timestamp(365)
        status = random.choices(ORDER_STATUSES, weights=status_weights)[0]
        delivery_point_id = 'NULL' if random.random() < 0.20 else str(random.choice(EXISTING_DELIVERY_POINTS))
        price = 'NULL' if random.random() < 0.10 else str(random.randint(100, 500000))

        # JSONB metadata (15% NULL)
        if random.random() < 0.15:
            metadata = 'NULL'
        else:
            metadata_data = {
                'source': random.choice(['web', 'mobile', 'api']),
                'pages_viewed': random.randint(1, 50),
                'session_duration': random.randint(10, 7200)
            }
            metadata = f"'{generate_jsonb(metadata_data)}'::jsonb"

        # TEXT[] tags (20% NULL)
        if random.random() < 0.20:
            tags = 'NULL'
        else:
            tag_list = []
            if random.random() > 0.5:
                tag_list.append('express')
            if random.random() > 0.7:
                tag_list.append('gift')
            if random.random() > 0.9:
                tag_list.append('vip')
            if tag_list:
                tags_array = ','.join(["'" + t + "'" for t in tag_list])
                tags = f"ARRAY[{tags_array}]::text[]"
            else:
                tags = "ARRAY[]::text[]"

        # TSTZRANGE delivery_window (40% NULL)
        delivery_window = 'NULL' if random.random() < 0.40 else generate_tsrange()

        # TEXT notes (50% NULL)
        if random.random() < 0.50:
            notes = 'NULL'
        else:
            notes = "'" + random.choice(['Без комментариев', 'Срочно', 'Подарок', 'Хрупкое']) + "'"

        rows.append(f"({order_id}, {user_id_val}, '{created_at}', '{status}', {delivery_point_id}, {price}, "
                    f"{metadata}, {tags}, {delivery_window}, {notes})")

    return rows


def generate_orderelem(count: int) -> List[str]:
    rows = []
    start_id = 53

    for i in range(count):
        elem_id = start_id + i
        order_id = random.randint(9, 300008)
        product_elem_id = random.randint(1, 250000)
        quantity = random.randint(1, 10)
        unit_price = random.randint(50, 100000)
        discount = random.choices([0, 5, 10, 15, 20], weights=[0.60, 0.15, 0.10, 0.10, 0.05])[0]

        rows.append(f"({elem_id}, {order_id}, {product_elem_id}, {quantity}, {unit_price}, {discount})")

    return rows


def generate_audit_log(count: int) -> List[str]:
    rows = []
    action_weights = [0.35, 0.35, 0.10, 0.10, 0.05, 0.05]

    tables = ['users', 'product', 'product_element', 'orders', 'orderelem',
              'cart', 'cartelem', 'payment', 'inventory', 'warehouse']
    table_weights = [0.10, 0.15, 0.25, 0.20, 0.15, 0.05, 0.05, 0.02, 0.02, 0.01]

    start_id = 8

    for i in range(count):
        log_id = start_id + i
        action = random.choices(AUDIT_ACTIONS, weights=action_weights)[0]
        table_name = random.choices(tables, weights=table_weights)[0]

        data_dict = {
            'entity_id': random.randint(1, 100000),
            'old_values': {'field1': random.randint(1, 1000)},
            'new_values': {'field1': random.randint(1, 1000)},
            'user_id': random.randint(1, 10000) if random.random() > 0.2 else None
        }
        data = generate_jsonb(data_dict)

        timestamp = generate_timestamp(365)
        user_id = 'NULL' if random.random() < 0.20 else str(random.randint(1, 10000))
        ip_address = 'NULL' if random.random() < 0.15 else "'" + generate_ip() + "'"

        rows.append(f"({log_id}, '{action}', '{table_name}', '{data}'::jsonb, '{timestamp}', {user_id}, {ip_address})")

    return rows


def generate_product_element(count: int) -> List[str]:
    rows = []
    colors = ['black', 'white', 'silver', 'gold', 'blue', 'red', 'green', 'purple', 'pink', 'gray']

    start_id = 24

    for i in range(count):
        elem_id = start_id + i

        # Skewed: 70% для 3 существующих продуктов
        if random.random() < 0.70:
            product_id = random.choice(EXISTING_PRODUCTS)
        else:
            product_id = random.randint(4, 1000)

        article_num = random.randint(10000, 999999)
        color = random.choice(colors)

        # Range цен с перекосом
        if random.random() < 0.70:
            price = random.randint(1000, 10000)
        elif random.random() < 0.90:
            price = random.randint(10000, 50000)
        else:
            price = random.randint(50000, 500000)

        # JSONB attributes (20% NULL)
        if random.random() < 0.20:
            attributes = 'NULL'
        else:
            attributes_data = {
                'size': random.choice(['S', 'M', 'L', 'XL', None]),
                'weight': round(random.uniform(0.1, 5.0), 2),
                'tags': ['tag_' + str(random.randint(1, 50)) for _ in range(random.randint(0, 5))]
            }
            attributes = "'" + generate_jsonb(attributes_data) + "'::jsonb"

        # INTEGER stock_level (15% NULL)
        stock_level = 'NULL' if random.random() < 0.15 else str(random.randint(0, 10000))

        # INTEGER supplier_id (30% NULL, Skewed)
        if random.random() < 0.30:
            supplier_id = 'NULL'
        elif random.random() < 0.70:
            supplier_id = str(random.randint(1, 10))
        else:
            supplier_id = str(random.randint(1, 100))

        rows.append(f"({elem_id}, {product_id}, {article_num}, '{color}', {price}, {attributes}, "
                    f"{stock_level}, {supplier_id})")

    return rows


def generate_sql_file(output_path: str = 'V3__insert_data.sql'):
    sql_lines = []
    batch_size = 10000

    # orders
    sql_lines.append("-- orders (~300,000 строк)")
    sql_lines.append(
        "INSERT INTO orders (id, user_id, created_at, status, delivery_point_id, price, metadata, tags, delivery_window, notes) VALUES")
    rows = generate_orders(TABLES_CONFIG['orders'])
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        sql_lines.append(',\n'.join(batch) + ';')
        sql_lines.append('')
    print(f"orders: {TABLES_CONFIG['orders']:,} строк")

    # orderelem
    sql_lines.append("-- orderelem (~320,000 строк)")
    sql_lines.append("INSERT INTO orderelem (id, order_id, elem_id, quantity, unit_price, discount) VALUES")
    rows = generate_orderelem(TABLES_CONFIG['orderelem'])
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        sql_lines.append(',\n'.join(batch) + ';')
        sql_lines.append('')
    print(f"orderelem: {TABLES_CONFIG['orderelem']:,} строк")

    # audit_log
    sql_lines.append("-- audit_log (~280,000 строк)")
    sql_lines.append("INSERT INTO audit_log (id, action, table_name, data, timestamp, user_id, ip_address) VALUES")
    rows = generate_audit_log(TABLES_CONFIG['audit_log'])
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        sql_lines.append(',\n'.join(batch) + ';')
        sql_lines.append('')
    print(f"audit_log: {TABLES_CONFIG['audit_log']:,} строк")

    # product_element
    sql_lines.append("-- product_element (~250,000 строк)")
    sql_lines.append(
        "INSERT INTO product_element (id, product_id, article_num, color, price, attributes, stock_level, supplier_id) VALUES")
    rows = generate_product_element(TABLES_CONFIG['product_element'])
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        sql_lines.append(',\n'.join(batch) + ';')
        sql_lines.append('')
    print(f"product_element: {TABLES_CONFIG['product_element']:,} строк")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))

    print(f"\nSQL файл создан: {output_path}")
    print(f"Общий объём: {sum(TABLES_CONFIG.values()):,} строк")


if __name__ == '__main__':
    generate_sql_file()
    print("\nГенерация завершена!")