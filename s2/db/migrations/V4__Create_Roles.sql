CREATE ROLE app_readonly WITH LOGIN PASSWORD 'readonly_pass_123';
GRANT CONNECT ON DATABASE shopdb TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

CREATE ROLE app_order_manager WITH LOGIN PASSWORD 'order_mgr_pass_123';
GRANT CONNECT ON DATABASE shopdb TO app_order_manager;
GRANT USAGE ON SCHEMA public TO app_order_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_order_manager;
GRANT SELECT, INSERT, UPDATE ON orders, orderelem TO app_order_manager;
GRANT SELECT, UPDATE ON payment, cart, cartelem TO app_order_manager;

CREATE ROLE app_inventory_manager WITH LOGIN PASSWORD 'inv_mgr_pass_123';
GRANT CONNECT ON DATABASE shopdb TO app_inventory_manager;
GRANT USAGE ON SCHEMA public TO app_inventory_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_inventory_manager;
GRANT SELECT, INSERT, UPDATE, DELETE ON inventory TO app_inventory_manager;
GRANT SELECT, UPDATE ON product_element TO app_inventory_manager;