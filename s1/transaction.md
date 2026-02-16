1. Commit

1.1 - Добавьте новый товар на склад и обновите количество на складе.
Итог — изменения сохранены.

    begin;
    insert into orderelem(order_id, elem_id, quantity, unit_price, discount)
    VALUES (1, 3, 1, 4000, 0);
    update orders set price = price + 52000 where id = 1;
    commit;

![](s1/images/4_1.png)

1.1b Добавьте новый пункт доставки и попробуйте изменить заказ
Итог — изменения сохранены.

    BEGIN;
    INSERT INTO inventory (elem_id, warehouse_id, quantity)
    VALUES (
    (SELECT id FROM product_element WHERE product_id = 1 AND color = 'purple'),
        2,
        20
    );
    UPDATE inventory
    SET quantity = quantity - 5
    WHERE elem_id = (SELECT id FROM product_element WHERE product_id = 1 AND color = 'purple')
    AND warehouse_id = 2;
    COMMIT;

![](s1/images/4_1b_1.png)
![](s1/images/4_1b_2.png)

2. Rollback

2.1 Добавление записи и обновление связной таблицы c откатом
Итог - данные не обновились

    begin;
    insert into orderelem(order_id, elem_id, quantity, unit_price, discount)
    VALUES (1, 3, 1, 4000, 0);
    update orders set price = price + 52000 where id = 1;
    rollback;

![](s1/images/4_2.png)

2.1b Добавьте новый пункт доставки и попробуйте изменить заказ, затем выполните откат.
Итог - данные не обновились

    BEGIN;
    INSERT INTO inventory (elem_id, warehouse_id, quantity)
    VALUES (
    (SELECT id FROM product_element WHERE product_id = 1 AND color = 'purple'),
        2,
        20
    );
    UPDATE inventory
    SET quantity = quantity - 5
    WHERE elem_id = (SELECT id FROM product_element WHERE product_id = 1 AND color = 'purple')
    AND warehouse_id = 2;
    rollback;

![](s1/images/4_2b_1.png)
![](s1/images/4_2b_2.png)

3. Неявный вызов rollback

3.1 Добавление с ошибкой
Итог - данные не сохранились из-за ошибки.

    begin;
    insert into orderelem(order_id, elem_id, quantity, unit_price, discount)
    VALUES (1, 3, 1/0, 4000, 0);
    update orders set price = price + 52000 where id = 1;
    commit;

![](s1/images/4_3.png)

3.1b При попытке добавить пользователя возникла ошибка. Итог — пользователь не был добавлен.
Итог - данные не сохранились из-за ошибки.

    begin;
    insert into users(name, login, password, created_at, role_id)
    values ('Тест', 'test_login', 'pass', now(), 1/0);
    commit;

![](s1/images/4_3b.png)

4. Dirty read (read uncomitted)

4.1 Чтение незакомиченного обновления цены
Итог - вывелась цена прежняя

    begin;
    update orders set price = price + 10000 where id = 1;
    ---
    begin;
    select price from orders where id = 1;
    commit;

![](s1/images/4_4.png)

4.1b Один пользователь обновляет количество товара в корзине, другой параллельно читает это значение. (параллельно) Итог вывелись старые данные, после коммит 1 и заново вызова второго данные новые

    begin;
    update cartElem set quantity = quantity + 2 where id = 1;
    ---
    begin;
    select *, CURRENT_TIMESTAMP from cartElem;
    commit;

![](s1/images/4_4b.png)

5. Non-repeatable read (read commited)

5.1 Обновление заказа
Итог - При первом селекте выводится 11300 при втором 31300

    begin;
    update orders set price = price + 20000 where id = 1;
    commit;
    ---
    begin;
    select price from orders where id = 1;
    select price from orders where id = 1;

![](s1/images/4_5.png)

5.1b Изменили роль пользователя, потом селектим ее.

    --- t1
    begin;
    SELECT role_id from users where id=1;

    --- t2
    begin;
    UPDATE users SET role_id = 2 WHERE id = 1;
    COMMIT;

    --- t1
    begin;
    SELECT role_id from users where id=1;
    SELECT role_id from users where id=1;
    commit; --- значение изменилось

![](s1/images/4_5b_1.png)
![](s1/images/4_5b_2.png)

6. (НЕ) Phantom read (repeatable read)

6.1 Обновление заказа
Итог - в отличие от предыдущего значение не менялось, в постгрес фантомных строк при repeatable read не возникает, строки появляются только после коммита

    begin;
    update orders set price = price + 20000 where id = 1;
    insert into orders(user_id, status, delivery_point_id, price)
    values (1, 'NEW', 1, 1000);
    commit;
    ---
    begin;
    select price from orders;

![](s1/images/4_6.png)

6.1b Один пользователь добавляет новый элемент в заказ, другой параллельно делает селекты.

    BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SELECT COUNT(*) FROM orderelem WHERE order_id = 2;

    BEGIN;
    INSERT INTO orderelem(order_id, elem_id, quantity, unit_price, discount)
    VALUES (2, 6, 1, 3800, 0);
    COMMIT;

    BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SELECT COUNT(*), CURRENT_TIMESTAMP FROM orderelem WHERE order_id = 2;
    SELECT COUNT(*), CURRENT_TIMESTAMP FROM orderelem WHERE order_id = 2;
    COMMIT;

2-й SELECT, при REPEATABLE READ покажет то же значение

![](s1/images/4_6b.png)

7. Serializable

7.1 Конкурентное изменение данных
Итог - вставка произошла только одна.

    begin;
    update orderelem set quantity = quantity + 1 where id = 12;
    select quantity from orderelem where id = 12;
    ---
    begin;
    update orderelem set quantity = quantity + 1 where id = 12;
    select quantity from orderelem where id = 12;

![](s1/images/4_7.png)

7.1b Два пользователя пытаются одновременно забронировать одинаковый элемент в корзине. Вставка произошла только одна, другая ошибка.

    BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    UPDATE cartElem SET quantity = quantity + 1 WHERE id = 1;
    SELECT quantity FROM cartElem WHERE id = 1;
    ---
    BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    UPDATE cartElem SET quantity = quantity + 1 WHERE id = 1;
    SELECT quantity FROM cartElem WHERE id = 1;
    COMMIT;

![](s1/images/4_7b.png)

8. Savepoint

8.1 Увеличение цены заказа
Итог - в первом случае только две команды выполняются во втором одна

    begin;
    update orders set price = price + 100 where id = 4;
    savepoint svp1;
    update orders set price = price + 100 where id = 4;
    savepoint svp2;
    update orders set price = price + 100 where id = 4;
    rollback to savepoint svp1;
    select price from orders where id = 4;
    commit;

    begin;
    update orders set price = price + 100 where id = 4;
    savepoint svp1;
    update orders set price = price + 100 where id = 4;
    savepoint svp2;
    update orders set price = price + 100 where id = 4;
    rollback to savepoint svp2;
    select price from orders where id = 4;
    commit;

![](s1/images/4_81.png)

![](s1/images/4_82.png)

8.1b Перемещение товара с двух промежуточных точек откатом к разным savepoint.

    begin;
    update inventory set quantity = quantity - 5 where elem_id = 3 and warehouse_id = 1;
    savepoint moved_from_1;
    update inventory set quantity = quantity + 5 where elem_id = 3 and warehouse_id = 2;
    savepoint moved_to_2;
    update inventory set quantity = quantity - 2 where elem_id = 3 and warehouse_id = 2;
    rollback to savepoint moved_from_1;
    select * from inventory where elem_id = 3;
    commit;

    begin;
    update inventory set quantity = quantity - 5 where elem_id = 3 and warehouse_id = 1;
    savepoint moved_from_1;
    update inventory set quantity = quantity + 5 where elem_id = 3 and warehouse_id = 2;
    savepoint moved_to_2;
    update inventory set quantity = quantity - 2 where elem_id = 3 and warehouse_id = 2;
    rollback to savepoint moved_to_2;
    select * from inventory where elem_id = 3;
    commit;

1. Уменьшение количества на складе 1
2. Увеличение количества на складе 2
3. Уменьшение количества на складе 2

В первом случае осталось ток первое обновление, во втором случае ток первое и второе обновление

![](s1/images/4_8b_1.png)
![](s1/images/4_8b_2.png)
![](s1/images/4_8b_3.png)
