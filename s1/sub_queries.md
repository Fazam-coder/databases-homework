1. SELECT

1.1 Вывести продукт и количество его вариаций

    select name, (select count(*) from product_element pe where pe.product_id = p.id) as cnt
    from product p;

![](s1/images/2_1_1.png)

1.2 Для каждого пользователя (users) выведи его имя и общее количество сделанных им заказов.﻿)

    select users.name, (select count(*) from orders where orders.user_id = users.id) as cnt
    from users;

![](s1/images/2_1_2.png)

1.3 Вывести список всех пользователей с их последним заказом (дата и статус), если заказ был сделан.
```
select u.name, u.login,
    (select o.created_at from orders o where o.user_id = u.id order by o.created_at desc limit 1) AS last_order_date,
    (select o.status from orders o where o.user_id = u.id order by o.created_at desc limit 1) AS last_order_status
from users u;
```

![](s1/images/2_1_3.png)

2. FROM

2.1 Вывести юзера и общую сумму его заказов

    select t.user_id, t.total_sum
    from (select user_id, sum(orders.price) as total_sum from orders group by user_id) t;

![](s1/images/2_2_1.png)

2.2 Все заказы, сделанные пользователями с ролью 'admin', используя подзапрос для создания временной
таблицы с ID администраторов.

    select * from orders join (select users.id from users join role on users.role_id = role.id
    where role.name = 'ADMIN') AS admin_users ON admin_users.id = orders.user_id;

![](s1/images/2_2_2.png)

2.3 Показать склады и общее количество товаров на каждом.
```
select w.name, stock.total_items
from warehouse w
join (
    select warehouse_id, sum(quantity) as total_items
    from inventory
    group by warehouse_id
) as stock on w.id = stock.warehouse_id;
```

![](s1/images/2_2_3.png)

3. WHERE

3.1 Вывести юзеров, которые совершали заказ

    select u.name from users u where u.id in (select o.user_id from orders o);

![](s1/images/2_3_1.png)

3.2 Покажи все товары (product), которые принадлежат категориям, в названии которых есть слово 'Phone')

    select * from product where category_id IN (select category.id from category
    where category.name = 'Phone');

![](s1/images/2_3_2.png)

3.3 Найти всех пользователей, которые делали заказы на сумму больше, чем средняя сумма всех заказов.
```
select distinct u.*
from users u join orders o on u.id = o.user_id
where o.price > (select avg(price) from orders);
```

![](s1/images/2_3_3.png)

4. HAVING

4.1 Вывести юзеров и среднюю цену заказов, где таковая больше чем минимальный товар

    select c.name, avg(Pe.price) from category c
    join Product P on c.id = P.category_id
    join Product_element Pe on P.id = Pe.product_id
    group by c.name
    having avg(pe.price) > (select min(pee.price) from product_element pee);

![](s1/images/2_4_1.png)

4.2 Найди ID категорий, в которых количество товаров больше или равно, чем среднее
количество товаров по всем категориям.

    SELECT category_id FROM product GROUP BY category_id
    HAVING COUNT(id) >= (SELECT AVG(product_count)
    FROM (SELECT COUNT(id) AS product_count
    FROM product GROUP BY category_id) AS counts_per_category);

![](s1/images/2_4_2.png)

4.3 Заказы, у которых количество позиций выше среднего числа позиций в заказе.
```
select o.id, o.created_at
from orders o join orderelem oe on o.id = oe.order_id
group by o.id
having count(oe.elem_id) > (
    select avg(item_count) from (
        select count(*) as item_count
        from orderelem
        group by order_id
    ) as avg_items
);
```

![](s1/images/2_4_3.png)

5. ALL

5.1 Вывести артикул товаров, где цена больше чем все товары артикул которых начинается на 1

    select article_num from product_element
    where price > all (select price from product_element where article_num::text like '1%');

![](s1/images/2_5_1.png)

5.2 Найди все товарные элементы (product_element),
цена которых строго выше цены каждого элемента, принадлежащего продукту с ID 10)

    SELECT * FROM product_element WHERE price >
    ALL (SELECT price FROM product_element WHERE product_id = 1);

![](s1/images/2_5_2.png)

5.3 Склады, где количество каждого элемента больше, чем на любом другом складе.
```
select distinct w.*
from warehouse w join inventory i on w.id = i.warehouse_id
where i.quantity > all (
    select i2.quantity
    from inventory i2
    where i2.elem_id = i.elem_id and i2.warehouse_id != w.id
);
```

![](s1/images/2_5_3.png)

6. IN

6.1 Вывести артикул товаров, где цена такая же как и в товарах с артикулом начинающимся на 2

    select article_num from product_element
    where price in (select price from product_element where article_num::text like '2%');

![](s1/images/2_6_1.png)

6.2 Покажи имена пользователей (users), которые сделали хотя бы один заказ.

    select name from users where users.id in (select user_id from orders);

![](s1/images/2_6_2.png)

6.3 Заказы с хотя бы одним элементом, имеющимся на складе.
```
select distinct o.*
from orders o join orderelem oe on o.id = oe.order_id
where oe.elem_id in (
    select elem_id from inventory where quantity > 0
);
```

![](s1/images/2_6_3.png)

7. ANY

7.1 Вывести артикул товаров, где цена больше чем хотя бы один товар артикул которого начинается на 2

    select article_num, price from product_element
    where price > any (select price from product_element where article_num::text like '2%');

![](s1/images/2_7_1.png)

7.2 Найди товары (product_element), цена которых больше, чем цена хотя бы одного товара
на складе (warehouse) с названием 'пункт 1')

    select * from product_element where price > any (select p.price from product_element p
    join inventory i on p.id = i.elem_id join warehouse w on i.warehouse_id = w.id
    where w.name = 'пункт 1');

![](s1/images/2_7_2.png)

7.3 Пользователи с хотя бы одним заказом со статусом “CANCELED”.
```
select distinct u.* from users u
where u.id = any (
    select distinct o.user_id
    from orders o
    where o.status = 'CANCELED'
);
```

![](s1/images/2_7_3.png)

8. EXIST

8.1 Вывести артикул товаров, которые появлялись в заказах

    select pe.article_num, pe.price from product_element pe
    where exists (select 1 from orderelem o where product_id = pe.id);

![](s1/images/2_8_1.png)

8.2 Найди всех пользователей (users), у которых есть хотя бы один заказ
со статусом 'PAID')

    SELECT id, name FROM users u WHERE EXISTS (SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.status = 'PAID');

![](s1/images/2_8_2.png)

8.3 Показать все товары, которые кто-то когда-то заказывал.
```
select distinct p.* from product p
where exists (
    select 1
    from product_element pe join orderelem oe on pe.id = oe.elem_id
    where pe.product_id = p.id
);
```

![](s1/images/2_8_3.png)

9. Сравнение по нескольким столбцам

9.1 Вывести артикул товаров, где цена такая же как и в товарах с артикулом начинающимся на 2 и цена больше 50к

    select article_num, price from product_element
    where (article_num, price) in (select article_num, price from product_element
    where article_num::text like '2%' and price > 50000);

![](s1/images/2_9_1.png)

9.2 Найди позиции в корзине (cartitem), которые полностью совпадают по ID
товарного элемента и количеству с какой-либо позицией в заказе с ID 1)

    SELECT * FROM cartelem c WHERE (c.elem_id, c.quantity) IN (SELECT elem_id,
    quantity FROM orderelem WHERE order_id = 1);

![](s1/images/2_9_2.png)

9.3 Найти заказы, которые полностью повторяют состав корзины какого-либо пользователя (по elem_id и quantity).
```
select distinct o.* from orders o
inner join orderelem oe on o.id = oe.order_id
where (oe.elem_id, oe.quantity) in (
    select ce.elem_id, ce.quantity
    from cartelem ce
);
```

![](s1/images/2_9_3.png)

10. Коррелированные подзапросы

10.1 Посчитать сколько подтипов у каждого продукта

    select name, (select count(*) from product_element pe where pe.product_id = p.id) as cnt from product p;

![](s1/images/2_10_1.png)

10.2 Для каждого заказа (orders) выведи его ID и стоимость, а также среднюю
стоимость всеx заказов, сделанных тем же самым пользователем.

    select id, price, (select avg(o.price) from orders o where o.user_id = user_id) from orders;

![](s1/images/2_10_2.png)

10.3 Найди все товарные элементы (product_element), цена которых является максимальной среди всех элементов,
относящихся к тому же самому головному товару (product).

    select * from product_element p1 where p1.price > (select max(p2.price)
    from product_element p2 where p1.id != p2.id and p2.product_id = p1.product_id)

![](s1/images/2_10_3.png)

10.4 Для каждого товара вывести его название и цену самого дорогого элемента.
```
select p.name,
    (select max(pe.price) from product_element pe
     where pe.product_id = p.id) as max_element_price
from product p;
```
![](s1/images/2_10_4.png)

10.5 Элементы, которые есть в наличии хотя бы на одном складе
```
select pe.id, pe.product_id, pe.article_num from product_element pe
where exists (
    select 1 from inventory i
    where i.elem_id = pe.id and i.quantity > 0
);
```

![](s1/images/2_10_5.png)
