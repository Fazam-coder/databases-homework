1. Выборка всех данных из таблицы

  1.1 Вывести всех пользователей

    select * from users;

  ![](s1/images/_1.1.png)  
    
  1.2 Вывести всех пользователей с их ролями

    select * from users join role on users.role_id = role.id;

  ![](s1/images/_1.2.png)

2. Выборка отдельных столбцов / присвоение новых имён столбцам

  2.1 Вывести имена пользователей

    select name as user_name, login from users;

  ![](s1/images/_2.1.png)  

  2.2 Вывести имена пользователей и название их роли

    select u.name as user_name, r.name as role_name from users u
    join role r on u.role_id=r.id;  

  ![](s1/images/_2.2.png)  

3. Выборка данных с созданием вычисляемого столбца

  3.1 Вернуть итоговые цены заказов деленые на 10

    select id, price / 10 as disc from orders;

  ![](s1/images/_3.1.png)  

  3.2 Расчитать итоговую стоимость товаров в заказах

    select p.article_num, o.quantity * o.unit_price - (o.discount / 100 * o.quantity * o.unit_price) as total from orderelem o
    join product_element p on o.elem_id=p.id;  

  ![](s1/images/_3.2.png)  

4.Выборка данных - математические функции

  4.1 Вернуть округлённую цену корзины

    select round(cart.price) as prc from cart;

  ![](s1/images/_4.1.png)  

  4.2 Вернуть округлённую цену корзины и имя владельца (right join)

    select users.name, round(cart.price) from cart right join users on cart.user_id=users.id;

  ![](s1/images/_4.2.png)

5. Выборка данных - логические функции
  
  5.1 В зависимости от количества делать скидку на общую сумму

    select id, unit_price, case
    when quantity = 1 then unit_price * 0.7
    when quantity > 2 then unit_price * 0.5
    else unit_price
    end as price from orderelem;

  ![](s1/images/_5.1.png)

  5.2 В зависимости от роли выводить ее описание

    select users.name, case
    when role.name = 'USER' then 'default account'
    when role.name = 'ADMIN' then 'premium account'
    end as role
    from users
    join role on users.role_id = role.id; 

  ![](s1/images/_5.2.png)

6. Выборка данных по условию / логические операции

  6.1 Выбрать товары с ценой более 5000

    select article_num, price from product_element
    where price > 5000;

  ![](s1/images/_6.1.png)  

  6.2 Вывести название товара, его количество и цену если он взять в 1 штуке и цена у него меньше 5000

    select product.name, orderelem.quantity, Product_element.price from orderelem
    join product_element on orderelem.elem_id=product_element.id
    join product on product_element.product_id = product.id
    where quantity = 1 and Product_element.price > 5000;  

  ![](s1/images/_6.2.png)

7. Выборка данных BETWEEN

  7.1 Выбрать товар с ценой между 4000 и 50000

    select article_num, price from product_element
    where price between 4000 and 50000;

  ![](s1/images/_7.1.png)

  7.2 Вывести информацию о товаре, количество которых в диапазоне от 1 до 2.

    select product.name, orderelem.quantity, Product_element.price from orderelem
    join product_element on orderelem.elem_id=product_element.id
    join product on product_element.product_id = product.id
    where quantity between 1 and 2;

  ![](s1/images/_7.2.png)

8. Выборка данных IN

  8.1 Выбираем транзации наличными или сбп

    select transaction_id, method from payment where method in ('cash', 'sbp');

  ![](s1/images/_8.1.png)

  8.2 Выбираем адреса в заказах и время их создания двух типов (left join)

    select address from delivery_point
    left join orders on delivery_point.id=orders.delivery_point_id
    where method in ('pickup', 'delivery');

  ![](s1/images/_8.2.png)

9. Выборка с сортировкой

  9.1 Выбрать заказы с ценой по убыванию

    select id, price from orders order by price desc;

  ![](s1/images/_9.1.png)

  9.2 Вывесьт элементы корзины юзера 1 с порядком убывания цены

    select product.name, product_element.article_num, product_element.price from cartelem
    join product_element on cartelem.elem_id=product_element.id
    join product on product_element.product_id = product.id
    where cartelem.cart_id = 1 order by product_element.price;

  ![](s1/images/_9.2.png)

10. Выборка данных - оператор LIKE

  10.1 Выбрать юзеров в именах которых есть "a"

    select name from users
    where name like '%а%';

  ![](s1/images/_10.1.png)

  10.2 Выбрать юзеров с именем длиной 6 и посмотреть их возможные роли (cross join)

    select users.name, role.name from users cross join role
    where users.name like '______';

  ![](s1/images/_10.2.png)

11. Выбор уникальынх элементов столбца

  11.1 Выбрать все возможные использованные цвета

    select distinct color from product_element;

  ![](s1/images/_11.1.png)

  11.2 Вывести все возможные методы доставки из заказов

    select distinct  delivery_point.method from orders
    join delivery_point on orders.delivery_point_id = delivery_point.id;

  ![](s1/images/_11.2.png)

12. Выбор ограниченного количества возвращаемых строк

  12.1 Выбрать 2 и 3 юзера сортированных по алфавиту

    select name from users order by name limit 2 offset 1;
    
  ![](s1/images/_12.1.png)
  
  12.2 Выбрать 2 и 3 адрес доставки из заказов (заказы выводятся даже если не выбран адрес, адреса также выводятся) (full join)
  
    select address, orders.created_at from delivery_point
    full join orders on delivery_point.id=orders.delivery_point_id
    order by orders.created_at
    limit 2 offset 1;

  ![](s1/images/_12.2.png)  
