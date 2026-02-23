import random
import json
from datetime import datetime, timedelta


EXISTING = {
    'role': [1, 2],
    'category': [1, 2, 3, 4, 5],
    'users': [1, 2, 3, 4, 5, 6],
    'product': [1, 2, 3],
    'product_element': list(range(1, 24)),
    'warehouse': [1, 2, 3],
    'delivery_point': [1, 2, 3],
    'orders': [1, 2, 3, 4, 5, 6, 7],
    'orderelem': list(range(1, 53)),
    'cart': [1, 3],
    'payment_method': ['cash', 'card', 'sbp'],
}

COUNT_PRODUCT_ELEMENT = 250_000
COUNT_ORDERS = 300_000
COUNT_ORDERELEM = 320_000
COUNT_AUDIT_LOG = 280_000
COUNT_USERS = 1000
COUNT_PRODUCTS = 500
COUNT_PAYMENT = 200_000

ORDER_STATUSES = ['new', 'processing', 'paid', 'shipped', 'delivered', 'cancelled']
AUDIT_ACTIONS = ['BEFORE_INSERT', 'AFTER_INSERT', 'BEFORE_UPDATE', 'AFTER_UPDATE', 'BEFORE_DELETE', 'AFTER_DELETE']
AUDIT_TABLES = ['users', 'product', 'product_element', 'orders', 'orderelem', 'cart', 'cartelem', 'payment',
                'inventory', 'warehouse']
PAYMENT_STATUSES = ['pending', 'paid', 'failed', 'refunded']

SEARCH_WORDS = [
    'телефон', 'наушники', 'часы', 'браслет', 'умный', 'беспроводной',
    'быстрый', 'мощный', 'компактный', 'лёгкий', 'прочный', 'стильный',
    'купить', 'заказать', 'цена', 'скидка', 'акция', 'новинка', 'хит'
]


def generate_timestamp(days_back=365):
    delta = timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59),
                      seconds=random.randint(0, 59))
    return (datetime.now() - delta).strftime('%Y-%m-%d %H:%M:%S')


def generate_jsonb(data):
    return json.dumps(data, ensure_ascii=False).replace("'", "''")


def generate_tstzrange():
    start = generate_timestamp(30)
    end_delta = random.randint(1, 48)
    end = datetime.strptime(start, '%Y-%m-%d %H:%M:%S') + timedelta(hours=end_delta)
    return "tstzrange('" + start + "', '" + end.strftime('%Y-%m-%d %H:%M:%S') + "', '[)')"


def generate_ip():
    return str(random.randint(1, 254)) + '.' + str(random.randint(0, 254)) + '.' + str(
        random.randint(0, 254)) + '.' + str(random.randint(1, 254))


def generate_keywords(words_count=10):
    words = random.sample(SEARCH_WORDS, min(words_count, len(SEARCH_WORDS)))
    return ', '.join(words)


def generate_users(start_id=7, count=COUNT_USERS):
    rows = []
    user_ids = list(EXISTING['users'])

    for i in range(count):
        uid = start_id + i
        user_ids.append(uid)
        role_id = random.choice(EXISTING['role'])
        rows.append("(" + str(uid) + ", 'User_" + str(uid) + "', 'user" + str(uid) + "@test.com', 'hash_" + str(
            uid) + "', '" + generate_timestamp() + "', " + str(role_id) + ")")

    return rows, user_ids


def generate_products(start_id=4, count=COUNT_PRODUCTS, category_ids=EXISTING['category']):
    rows = []
    product_ids = list(EXISTING['product'])

    for i in range(count):
        pid = start_id + i
        product_ids.append(pid)
        category_id = random.choice(category_ids)
        name = "Product_" + str(pid) + " " + random.choice(SEARCH_WORDS)

        # JSONB characteristics
        if random.random() < 0.3:
            characteristics = 'NULL'
        else:
            char_data = {'brand': 'Test', 'year': random.randint(2020, 2025)}
            characteristics = "'" + generate_jsonb(char_data) + "'::jsonb"

        # TEXT description
        if random.random() < 0.2:
            description = 'NULL'
        else:
            desc_words = ' '.join(random.sample(SEARCH_WORDS, 5))
            description = "'Описание товара " + str(pid) + ". " + desc_words + "'"

        # TSVECTOR search_vector
        if random.random() < 0.10:
            search_vector = 'NULL'
        else:
            sv_words = name + " " + random.choice(SEARCH_WORDS) + " " + random.choice(SEARCH_WORDS)
            search_vector = "to_tsvector('russian', '" + sv_words + "')"

        # TEXT keywords
        if random.random() < 0.15:
            keywords = 'NULL'
        else:
            keywords = "'" + generate_keywords() + "'"

        rows.append("(" + str(pid) + ", " + str(
            category_id) + ", '" + name + "', " + characteristics + ", " + description + ", " + search_vector + ", " + keywords + ")")

    return rows, product_ids


def generate_product_elements(start_id=24, count=COUNT_PRODUCT_ELEMENT, product_ids=None):
    rows = []
    colors = ['black', 'white', 'silver', 'gold', 'blue', 'red', 'green', 'purple', 'pink', 'gray']

    used_combinations = set()

    for i in range(count):
        eid = start_id + i

        # Skewed: 70% для 3 существующих продуктов
        if random.random() < 0.70:
            product_id = random.choice(EXISTING['product'])
        else:
            product_id = random.choice(product_ids)

        max_attempts = 100
        for attempt in range(max_attempts):
            article_num = random.randint(10000, 999999)
            combo = (product_id, article_num)
            if combo not in used_combinations:
                used_combinations.add(combo)
                break
        else:
            article_num = 10000 + i

        color = random.choice(colors)
        price = random.randint(100, 500000)

        # JSONB attributes
        if random.random() < 0.20:
            attributes = 'NULL'
        else:
            attr_data = {
                'size': random.choice(['S', 'M', 'L', 'XL', None]),
                'weight': round(random.uniform(0.1, 5.0), 2),
                'tags': ['tag_' + str(random.randint(1, 50)) for _ in range(random.randint(0, 5))]
            }
            attributes = "'" + generate_jsonb(attr_data) + "'::jsonb"

        stock_level = 'NULL' if random.random() < 0.15 else str(random.randint(0, 10000))

        if random.random() < 0.30:
            supplier_id = 'NULL'
        elif random.random() < 0.70:
            supplier_id = str(random.randint(1, 10))
        else:
            supplier_id = str(random.randint(1, 100))

        # TSVECTOR search_vector
        if random.random() < 0.10:
            search_vector = 'NULL'
        else:
            sv_words = color + " артикул " + str(article_num) + " " + ' '.join(random.sample(SEARCH_WORDS, 3))
            search_vector = "to_tsvector('russian', '" + sv_words + "')"

        rows.append("(" + str(eid) + ", " + str(product_id) + ", " + str(article_num) + ", '" + color + "', " + str(
            price) + ", " + attributes + ", " + stock_level + ", " + supplier_id + ", " + search_vector + ")")

    return rows


def generate_orders(start_id=9, count=COUNT_ORDERS, user_ids=None, delivery_point_ids=EXISTING['delivery_point']):
    rows = []
    order_ids = list(EXISTING['orders'])
    status_weights = [0.15, 0.25, 0.20, 0.15, 0.20, 0.05]

    for i in range(count):
        oid = start_id + i
        order_ids.append(oid)

        if random.random() < 0.15:
            user_id = 'NULL'
        elif random.random() < 0.70:
            user_id = str(random.choice([1, 2]))
        else:
            user_id = str(random.choice(user_ids))

        created_at = generate_timestamp(365)
        status = random.choices(ORDER_STATUSES, weights=status_weights)[0]

        if random.random() < 0.20:
            delivery_point_id = 'NULL'
        else:
            delivery_point_id = str(random.choice(delivery_point_ids))

        price = 'NULL' if random.random() < 0.10 else str(random.randint(100, 500000))

        # JSONB metadata
        if random.random() < 0.15:
            metadata = 'NULL'
        else:
            meta_data = {
                'source': random.choice(['web', 'mobile', 'api']),
                'pages_viewed': random.randint(1, 50),
                'session_duration': random.randint(10, 7200)
            }
            metadata = "'" + generate_jsonb(meta_data) + "'::jsonb"

        # TEXT[] tags
        if random.random() < 0.20:
            tags = 'NULL'
        else:
            tag_list = [t for t in ['express', 'gift', 'vip'] if random.random() > 0.5]
            if tag_list:
                tags_array = ','.join(["'" + t + "'" for t in tag_list])
                tags = "ARRAY[" + tags_array + "]::text[]"
            else:
                tags = "ARRAY[]::text[]"

        # TSTZRANGE delivery_window
        delivery_window = 'NULL' if random.random() < 0.40 else generate_tstzrange()

        # TEXT notes
        notes = 'NULL' if random.random() < 0.50 else "'" + random.choice(
            ['Без комментариев', 'Срочно', 'Подарок', 'Хрупкое']) + "'"

        # TSVECTOR search_vector
        if random.random() < 0.10:
            search_vector = 'NULL'
        else:
            sv_words = random.choice(SEARCH_WORDS) + " " + random.choice(SEARCH_WORDS) + " " + random.choice(
                SEARCH_WORDS)
            search_vector = "to_tsvector('russian', '" + sv_words + "')"

        rows.append("(" + str(
            oid) + ", " + user_id + ", '" + created_at + "', '" + status + "', " + delivery_point_id + ", " + price +
                    ", " + metadata + ", " + tags + ", " + delivery_window + ", " + notes + ", " + search_vector + ")")

    return rows, order_ids


def generate_orderelem(start_id=53, count=COUNT_ORDERELEM, order_ids=None, product_element_ids=None):
    """6. orderelem (FK → orders.id, product_element.id) + уникальность (order_id, elem_id)"""
    rows = []

    used_combinations = set()

    for i in range(count):
        eid = start_id + i

        max_attempts = 100
        for attempt in range(max_attempts):
            order_id = random.choice(order_ids)
            elem_id = random.choice(product_element_ids)
            combo = (order_id, elem_id)
            if combo not in used_combinations:
                used_combinations.add(combo)
                break
        else:
            continue

        quantity = random.randint(1, 10)
        unit_price = random.randint(50, 100000)
        discount = random.choices([0, 5, 10, 15, 20], weights=[0.60, 0.15, 0.10, 0.10, 0.05])[0]

        rows.append("(" + str(eid) + ", " + str(order_id) + ", " + str(elem_id) + ", " + str(quantity) + ", " + str(
            unit_price) + ", " + str(discount) + ")")

    return rows


def generate_audit_log(start_id=8, count=COUNT_AUDIT_LOG, user_ids=None):
    rows = []
    action_weights = [0.35, 0.35, 0.10, 0.10, 0.05, 0.05]
    table_weights = [0.10, 0.15, 0.25, 0.20, 0.15, 0.05, 0.05, 0.02, 0.02, 0.01]

    for i in range(count):
        log_id = start_id + i
        action = random.choices(AUDIT_ACTIONS, weights=action_weights)[0]
        table_name = random.choices(AUDIT_TABLES, weights=table_weights)[0]

        data_dict = {
            'entity_id': random.randint(1, 100000),
            'old': {'f1': random.randint(1, 1000)},
            'new': {'f1': random.randint(1, 1000)}
        }
        data = generate_jsonb(data_dict)

        timestamp = generate_timestamp(365)
        user_id = 'NULL' if random.random() < 0.20 else str(random.choice(user_ids))
        ip_address = 'NULL' if random.random() < 0.15 else "'" + generate_ip() + "'"

        rows.append("(" + str(
            log_id) + ", '" + action + "', '" + table_name + "', '" + data + "'::jsonb, '" + timestamp + "', " + user_id + ", " + ip_address + ")")

    return rows


def generate_payment(start_id=4, count=COUNT_PAYMENT, order_ids=None):
    rows = []
    status_weights = [0.20, 0.50, 0.20, 0.10]

    for i in range(count):
        pid = start_id + i
        order_id = random.choice(order_ids)
        status = random.choices(PAYMENT_STATUSES, weights=status_weights)[0]
        transaction_id = "'TX" + str(random.randint(100000000, 999999999)) + "'" if random.random() > 0.15 else 'NULL'
        paid_at = "'" + generate_timestamp() + "'" if status == 'paid' else 'NULL'
        method = random.choice(EXISTING['payment_method'])

        # JSONB payment_details
        if random.random() < 0.25:
            payment_details = 'NULL'
        else:
            payment_data = {
                'card_mask': '****' + str(random.randint(1000, 9999)),
                'installments': random.randint(0, 12),
                'cashback': random.randint(0, 1000)
            }
            payment_details = "'" + generate_jsonb(payment_data) + "'::jsonb"

        # TEXT[] fraud_flags
        if random.random() < 0.30:
            fraud_flags = 'NULL'
        else:
            flag_list = [t for t in ['high_amount', 'new_device', 'foreign_ip', 'velocity_check'] if
                         random.random() > 0.7]
            if flag_list:
                flags_array = ','.join(["'" + t + "'" for t in flag_list])
                fraud_flags = "ARRAY[" + flags_array + "]::text[]"
            else:
                fraud_flags = "ARRAY[]::text[]"

        processing_time_ms = 'NULL' if random.random() < 0.10 else str(random.randint(10, 10000))

        rows.append("(" + str(pid) + ", " + str(
            order_id) + ", '" + status + "', " + transaction_id + ", " + paid_at + ", '" + method + "', " +
                    payment_details + ", " + fraud_flags + ", " + processing_time_ms + ")")

    return rows


def write_inserts(f, table, columns, rows, batch_size=10000):
    f.write("-- " + table + " (" + str(len(rows)) + " строк)\n")
    f.write("INSERT INTO " + table + " (" + columns + ") VALUES\n")

    total_batches = (len(rows) + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(rows))
        batch = rows[start:end]

        if batch_idx == total_batches - 1:
            f.write(',\n'.join(batch) + ';\n\n')
        else:
            f.write(',\n'.join(batch) + ',\n')


def generate_sql_file(output_path='V3__insert_data.sql'):
    print("Генерация данных в порядке FK...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- FLYWAY MIGRATION: V3__insert_data.sql\n")
        f.write("-- Типы: JSONB, TEXT[], TSTZRANGE, TSVECTOR, INET\n\n")

        print("   users...")
        user_rows, user_ids = generate_users()
        write_inserts(f, 'users', 'id, name, login, password, created_at, role_id', user_rows)

        print("   product...")
        product_rows, product_ids = generate_products()
        write_inserts(f, 'product', 'id, category_id, name, characteristics, description, search_vector, keywords',
                      product_rows)

        print("   product_element...")
        pe_rows = generate_product_elements(product_ids=product_ids)
        write_inserts(f, 'product_element',
                      'id, product_id, article_num, color, price, attributes, stock_level, supplier_id, search_vector',
                      pe_rows)

        print("   orders...")
        order_rows, order_ids = generate_orders(user_ids=user_ids)
        write_inserts(f, 'orders',
                      'id, user_id, created_at, status, delivery_point_id, price, metadata, tags, delivery_window, notes, search_vector',
                      order_rows)

        print("   orderelem...")
        pe_ids = list(range(24, 24 + COUNT_PRODUCT_ELEMENT))
        oe_rows = generate_orderelem(order_ids=order_ids, product_element_ids=pe_ids)
        write_inserts(f, 'orderelem', 'id, order_id, elem_id, quantity, unit_price, discount', oe_rows)

        print("   payment...")
        payment_rows = generate_payment(order_ids=order_ids)
        write_inserts(f, 'payment',
                      'id, order_id, status, transaction_id, paid_at, method, payment_details, fraud_flags, processing_time_ms',
                      payment_rows)

        print("   audit_log...")
        audit_rows = generate_audit_log(user_ids=user_ids)
        write_inserts(f, 'audit_log', 'id, action, table_name, data, timestamp, user_id, ip_address', audit_rows)

        total = COUNT_USERS + COUNT_PRODUCTS + COUNT_PRODUCT_ELEMENT + COUNT_ORDERS + COUNT_ORDERELEM + COUNT_PAYMENT + COUNT_AUDIT_LOG
    print("\nГотово: " + output_path)
    print("Всего строк: " + str(total))


if __name__ == '__main__':
    generate_sql_file()
    print("Завершено!")