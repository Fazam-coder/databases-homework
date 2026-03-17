INSERT INTO orders (id, user_id, status, price, created_at) VALUES
    (1, 3, 'completed', 50000, NOW() - INTERVAL '30 days'),
    (2, 3, 'processing', 25000, NOW() - INTERVAL '7 days'),
    (3, 4, 'new', 15000, NOW() - INTERVAL '1 day'),
    (4, 1, 'completed', 100000, NOW() - INTERVAL '60 days'),
    (5, 2, 'cancelled', 30000, NOW() - INTERVAL '14 days')
ON CONFLICT (id) DO UPDATE SET
    user_id = EXCLUDED.user_id,
    status = EXCLUDED.status,
    price = EXCLUDED.price;