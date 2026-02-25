## Использование ">" orders
``` sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id, user_id, status, price 
FROM orders 
WHERE price > 100000;
```
* Без индекса
![](images/2_1.png)
* С индексом b-tree
![](images/2_2.png)
* С индексом hash
![](images/2_3.png)

## Использование "<" product_element
``` sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, product_id, article_num, color, price
FROM product_element
WHERE price < 5000;
```
* Без индекса
  ![](images/2_4.png)
* С индексом b-tree
  ![](images/2_5.png)
* С индексом hash
  ![](images/2_6.png)

## Использование "=" orders
``` sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id, user_id, status, created_at, price 
FROM orders 
WHERE created_at = '2025-12-02'::timestamptz;
```
* Без индекса
  ![](images/2_7.png)
* С индексом b-tree
  ![](images/2_8.png)
* С индексом hash
  ![](images/2_9.png)

## Использование "%like" payment
``` sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT id, action, table_name, timestamp 
FROM audit_log 
WHERE table_name LIKE '%log';
```
* Без индекса
  ![](images/2_10.png)
* С индексом b-tree
  ![](images/2_11.png)
* С индексом hash
  ![](images/2_12.png)

## Использование "IN" audit_log
``` sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id, action, table_name, ip_address, timestamp 
FROM audit_log 
WHERE ip_address IN ('192.168.1.1', '192.168.1.2', '192.168.1.3', '10.0.0.1', '10.0.0.2');
```
* Без индекса
  ![](images/2_13.png)
* С индексом b-tree
  ![](images/2_14.png)
* С индексом hash
  ![](images/2_15.png)

## ДОП: Составной индекс (user_id, created_at) orders
``` sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id, user_id, status, created_at, price 
FROM orders 
WHERE user_id = 100 AND created_at >= '2025-06-01'::timestamptz;
```
* Без индекса
![](images/2_16.png)
* С индексом
![](images/2_17.png)
* Если только первый столбец
``` sql
WHERE user_id = 100
```
![](images/2_18.png)
* Если только второй столбец
``` sql
WHERE created_at >= '2025-06-01'::timestamptz;
```
![](images/2_19.png)