## Создание ролей и выдача прав:
![](images/1_2.png)
* `app_readonly` - роль только для чтения
* `app_order_manager` - роль для менеджера заказов
* `app_inventory_manager` - роль для управления складами
## Миграции:
![](images/1_3.png)
## Заливка данных
* Файл: `generate_data.py`
* Основные таблицы, куда были залиты данные: `orders`, `orderelem`, `audit_log`, `product_element`
## Пример работы с ролью:
![](images/1_1.png)