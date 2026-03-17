INSERT INTO product_element (id, product_id, price, article_num)
SELECT
    i,
    i,
    (500 + i * 100)::numeric(10,2),
    (10 + i * 5)::int
FROM generate_series(1, 10) AS i
ON CONFLICT (id) DO UPDATE SET
    product_id = EXCLUDED.product_id,
    price = EXCLUDED.price,
    article_num = EXCLUDED.article_num;