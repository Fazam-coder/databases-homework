# GIN
## 1. JSONB поле `audit_log.data` - оператор @>
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, action, table_name, data, timestamp
FROM audit_log
WHERE data @> '{"entity_id": 1000}';
```
![](images/3_1.png)
```sql
CREATE INDEX idx_audit_log_data_gin ON audit_log USING GIN (data);
```
![](images/3_2.png)
## 2. JSONB поле `audit_log.data` - оператор ?&
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, action, table_name, data
FROM audit_log
WHERE data ?& ARRAY['entity_id', 'old_values', 'new_values'];
```
![](images/3_3.png)
```sql
CREATE INDEX idx_audit_log_data_gin ON audit_log USING GIN (data);
```
![](images/3_4.png)
## 3. JSONB поле `product_element.attributes` - оператор ?
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, product_id, attributes
FROM product_element
WHERE attributes ? 'warranty_extended';
```
![](images/3_5.png)
```sql
CREATE INDEX idx_product_element_attributes_gin ON product_element USING GIN (attributes);
```
![](images/3_6.png)
## 4. JSONB поле `product_element.attributes` - оператор ?| (в результате много строк, поэтому Seq Scan)
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, product_id, attributes
FROM product_element
WHERE attributes ?| ARRAY['size', 'weight', 'tags'];
```
![](images/3_7.png)
```sql
CREATE INDEX idx_product_element_attributes_gin ON product_element USING GIN (attributes);
```
![](images/3_8.png)
## 5. JSONB поле `audit_log.data` оператор @> вложенный поиск
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, action, table_name, data
FROM audit_log
WHERE data @> '{"old_values": {"f1": 100}}';
```
![](images/3_9.png)
```sql
CREATE INDEX idx_audit_log_data_gin ON audit_log USING GIN (data);
```
![](images/3_10.png)

# GiST
## 1. TSTZRANGE поле `orders.delivery_window` оператор &&
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, delivery_window, created_at
FROM orders
WHERE delivery_window && tstzrange('2025-06-01', '2025-07-01');
```
![](images/3_11.png)
```sql
CREATE INDEX idx_orders_delivery_window_gist ON orders USING GiST (delivery_window);
```
![](images/3_12.png)
## 2. TSTZRANGE поле `orders.delivery_window` оператор @>
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, delivery_window
FROM orders
WHERE delivery_window @> '2025-06-15 12:00:00'::timestamptz;
```
![](images/3_13.png)
```sql
CREATE INDEX idx_orders_delivery_window_gist ON orders USING GiST (delivery_window);
```
![](images/3_14.png)
## 3. TSVECTOR поле `product.search_vector` оператор @@ to_tsquery
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, name, description, search_vector
FROM product
WHERE search_vector @@ to_tsquery('russian', 'realme');
```
![](images/3_15.png)
```sql
CREATE INDEX idx_product_name_gist ON product USING GiST (search_vector);
```
![](images/3_16.png)
## 4. TSVECTOR поле `product.search_vector` оператор @@ to_tsquery('...&...')
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, name, description
FROM product
WHERE search_vector @@ to_tsquery('russian', 'realme & pro');
```
![](images/3_17.png)
```sql
CREATE INDEX idx_product_name_gist ON product USING GiST (search_vector);
```
![](images/3_18.png)
## 5. TSVECTOR поле `product.search_vector` оператор @@ to_tsquery('...| !...') (в результате много строк, поэтому Seq Scan)
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, name, description
FROM product
WHERE search_vector @@ to_tsquery('russian', 'realme | !buds');
```
![](images/3_19.png)
```sql
CREATE INDEX idx_product_name_gist ON product USING GiST (search_vector);
```
![](images/3_20.png)

# JOIN
## 1. Hash JOIN
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id AS order_id, o.status, o.created_at, u.name AS user_name, u.login
FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE o.user_id IS NOT NULL;
```
![](images/3_21.png)
## 2. Merge JOIN
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id AS order_id, o.status, oe.elem_id, oe.quantity, oe.unit_price
FROM orders o
INNER JOIN orderelem oe ON o.id = oe.order_id
WHERE o.id > 10000;
```
![](images/3_22.png)
## 3. Nested Loop Memoize
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT oe.order_id, oe.quantity, pe.article_num, pe.color, pe.price
FROM orderelem oe
INNER JOIN product_element pe ON oe.elem_id = pe.id
WHERE oe.order_id > 10000
LIMIT 1000;
```
![](images/3_23.png)
## 4. Hash JOIN
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT pe.id AS elem_id, pe.article_num, pe.price, p.name AS product_name, p.category_id
FROM product_element pe
         INNER JOIN product p ON pe.product_id = p.id
WHERE pe.price > 10000;
```
![](images/3_24.png)
## 5. (то же, что и 4, только с LIMIT) Nested Loop Memoize
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT pe.id AS elem_id, pe.article_num, pe.price, p.name AS product_name, p.category_id
FROM product_element pe
INNER JOIN product p ON pe.product_id = p.id
WHERE pe.price > 10000
LIMIT 1000;
```
![](images/3_25.png)