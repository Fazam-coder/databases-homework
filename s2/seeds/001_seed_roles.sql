INSERT INTO role (id, name) VALUES
    (1, 'admin'),
    (2, 'manager'),
    (3, 'customer'),
    (4, 'guest')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name;