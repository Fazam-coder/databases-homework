Общие изменения:    
    
    alter table orders alter column total_price type integer;
    alter table orderelem alter column unit_price type integer;
    alter table orderelem alter column discount type integer;
    alter table orderelem alter column total_price type integer;
    alter table cart add constraint ch_login check ( (user_id is null and guest_token is not null) or (user_id is not null and guest_token isnull) );

Нарушение 3NF: метод получения товара являлся детерминантом для адреса, где метод зависил от id, то есть транзитивная зависимость. Решение: декомпозиция, а именно создание новой таблицы delivery_point. 

    create table delivery_point
    (
        id bigserial primary key,
        method varchar(64) not null ,
        address varchar(512),
        unique (method, address)
    );
    alter table orders add column delivery_point_id bigint references delivery_point(id);
    alter table orders drop column delivery_method;
    alter table orders drop column address;
    insert into delivery_point(method, address)
    values ('pickup', 'ул. А д. 2'),
           ('pickup', 'ул. И д. 12'),
           ('delivery', null);
    update orders
    set delivery_point_id = case id
    when 1 then 1
    when 2 then 2
    when 3 then 3 end
    where id in (1, 2, 3);

Нарушение 3NF: в данном контексте провайдер зависит от метода оплаты, значит есть транзитивная зависимость. Решение: декомпозиция в виде создание таблицы с методом и зависящим от него провайдером.

    create table payment_method (
         method varchar(32) primary key,
         provider varchar(64)
    );
    insert into payment_method(method, provider)
    select distinct method, provider
    from payment;
    alter table payment add constraint fk_payment_method foreign key (method) references payment_method(method);
    alter table payment drop column provider;
    update payment
    set method = case id
        when 1 then 'cash'
        when 2 then 'card'
        when 3 then 'sbp' end
    where id in (1, 2, 3);

Нарушение 3NF: в таблице элементов есть транзитивная зависимоть (скидка, цена, количество) -> сумма. Решение: удалить строку, так как в таблице заказов уже будет считаться сумма.

    alter table orders drop column total_price;