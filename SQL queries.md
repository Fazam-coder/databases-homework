create table Users (
    id serial,
    name varchar(32) not null,
    login varchar(64) unique,
    password varchar(64) not null,
    created_at date,
    role_id integer,
    constraint pk_id primary key (id),
    constraint fk_role_id foreign key (role_id) references Role(id) on UPDATE cascade on delete cascade
);

create table Role (
    id integer,
    name varchar(32) not null,
    constraint pk_role_id primary key (id)
);

create table Category (
    id integer,
    name varchar(32) not null,
    constraint pk_category_id primary key (id)
);

create table Product (
    id serial,
    category_id integer not null ,
    name varchar(128),
    characteristics jsonb,
    description text,
    constraint pk_product_id primary key (id),
    constraint fk_category_id foreign key (category_id) references Category(id)
);

create table Product_element(
    id serial,
    product_id integer not null,
    article_num integer not null,
    color varchar(32),
    price integer not null check ( price >= 0),
    attributes jsonb,
    constraint pk_product_element_id primary key (id),
    constraint fk_product_id foreign key (product_id) references Product(id) on UPDATE cascade on delete cascade,
    constraint unique_article unique (product_id, article_num)
);

create table Warehouse (
    id serial,
    name varchar(64) not null,
    address varchar(256) not null ,
    constraint pk_warehouse_id primary key (id)
);

create table inventory (
    elem_id integer not null,
    warehouse_id integer not null,
    quantity integer not null check (quantity >= 0),
    constraint pk_inventory primary key (elem_id, warehouse_id),
    constraint fk_elem_id foreign key (elem_id) references product_element(id) on update cascade on delete cascade,
    constraint fk_warehouse_id foreign key (warehouse_id) references warehouse(id) on update cascade on delete cascade
);

create table cart (
    id bigserial,
    user_id bigint,
    guest_token uuid,
    created_at timestamptz not null default now(),
    price decimal(12,2) not null default 0 check (price >= 0),
    constraint unique_cart_user_active unique (user_id),
    constraint unique_cart_guest unique (guest_token),
    constraint pk_cart_id primary key (id),
    constraint fk_user_id foreign key (user_id) references users(id) on update cascade on delete cascade
);

create table cartelem (
    id bigserial,
    cart_id bigint not null,
    elem_id bigint not null,
    quantity integer not null check (quantity > 0),
    constraint uq_cart_item unique (cart_id, elem_id),
    constraint pk_cart_elem_id primary key (id),
    constraint fk_cart_id foreign key (cart_id) references cart(id) on update cascade on delete cascade,
    constraint fk_elem_id foreign key (elem_id) references product_element(id) on update cascade on delete cascade
);

create table orders (
    id bigserial,
    user_id bigint,
    created_at timestamptz not null default now(),
    total_price decimal(12,2) not null check (total_price >= 0),
    status varchar(32) not null,
    delivery_method varchar(64),
    address varchar(512),
    constraint pk_orders_id primary key (id),
    constraint fk_user_id foreign key (user_id) references users(id) on update cascade on delete cascade
);

create table orderelem (
    id bigserial,
    order_id bigint not null,
    elem_id bigint not null,
    quantity integer not null check (quantity > 0),
    unit_price decimal(12,2) not null check (unit_price >= 0),
    discount decimal(12,2) not null default 0 check (discount >= 0),
    total_price decimal(12,2) not null check (total_price >= 0),
    constraint unique_order_item unique (order_id, elem_id),
    constraint pk_order_elem_id primary key (id),
    constraint fk_order_id foreign key (order_id) references orders(id) on update cascade on delete cascade,
    constraint fk_elem_id foreign key (elem_id) references product_element(id) on update cascade on delete cascade
);

create table payment (
    id bigserial,
    order_id bigint not null,
    method varchar(32) not null,
    status varchar(32) not null,
    provider varchar(64),
    transaction_id varchar(128),
    paid_at timestamptz,
    constraint unique_payment_order unique(order_id, transaction_id),
    constraint pk_payment_id primary key (id),
    constraint fk_order_id foreign key (order_id) references orders(id) on update cascade on delete cascade
);


alter table cartElem drop constraint cartelem_cart_id_fkey;

alter table category add constraint unique_category_name unique (name);

alter table users alter column created_at type timestamptz;

alter table users alter column created_at set default now();

alter table role rename constraint role_pkey to pk_role_id;


insert into users(name, login, password, role_id)
VALUES ('Кемал', 'kemal@gmail.com', '228337', 2),
       ('Булат', 'bulat@gmail.com', 'qwerty',  1),
       ('Тьютор', 'ilovemathanalysis@gmail.com', 'integrali', 1);

insert into Role
values (1, 'USER'),
       (2, 'ADMIN');

insert into Category
values (1, 'Phone'),
       (2, 'Band'),
       (3, 'Watch'),
       (4, 'Earphone'),
       (5, 'Scales');

insert into Product (category_id, name)
values (3, 'realme buds 6 pro'),
       (1, 'realme 15 pro'),
       (2, 'realme band 5');

insert into Product_element(product_id, article_num, color, price)
VALUES (1, 11, 'white', 4000),
       (2, 21, 'black', 50000),
       (2, 22, 'white', 50000);

insert into Warehouse(name, address)
VALUES ('пункт 1', 'ул. А д.1'),
       ('пункт 2', 'ул. С д.2');

insert into Inventory(elem_id, warehouse_id, quantity)
values (1, 1, 50),
       (2, 1, 49),
       (3, 1, 100);

INSERT INTO cart (user_id, guest_token, price)
VALUES (1, null, 1500),
       (null, 'a0d9a0b0-1e59-4f2e-99ea-111111111111', 650),
       (2, null, 300);

INSERT INTO cartElem (cart_id, elem_id, quantity)
VALUES (1, 1, 2),
       (1, 2, 1),
       (2, 2, 1);

INSERT INTO orders (user_id, total_price, status, delivery_method, address)
VALUES (1, 1800, 'NEW', 'courier', 'ул. Ф д. 4'),
       (2, 300, 'PAID', 'pickup', 'ул. Р д. 12'),
       (3, 800, 'Cancel', 'pickup', 'ул. W д. 6');

INSERT INTO orderElem (order_id, elem_id, quantity, unit_price, discount, total_price)
VALUES (1, 1, 2, 500, 0, 1000.00),
       (1, 2, 1, 800, 0, 800.00),
       (2, 2, 1, 300, 0, 300);

INSERT INTO payment (id, order_id, method, status, provider, transaction_id, paid_at)
VALUES (1, 2, 'card', 'paid', 'Mir', 'TX123456789', '2025-09-18 17:00:00+03'),
       (2, 3, 'sbp', 'pending', 'Sberbank', 'TX987654321', NULL),
       (3, 1, 'cash', 'failed', NULL, NULL, NULL);


UPDATE orders
SET status = 'CANCELED'
WHERE id = 3;

UPDATE product_element
SET price = 52000
WHERE id = 2;

UPDATE cartElem
SET quantity = quantity + 1
WHERE cart_id = 1 AND elem_id = 1;

UPDATE orders
SET delivery_method = 'pickup'
WHERE id = 1;

UPDATE payment
SET status = 'failed'
WHERE order_id = 3;
