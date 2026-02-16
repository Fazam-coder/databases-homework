1. Вернуть артикул и цену конкретного продукта с ценой между 1000 и 5000
> π<sub>article_num, price</sub> (σ<sub>price>1000^price<5000</sub> (Product_element))
2. Вернуть наименование товара, количество и итоговую цену по ID заказа.
> π<sub>Product.name,Order_elem.quantity,Order_elem.total_price</sub>
(σ<sub>Order_elem.order_id=?</sub>
(Order_elem ⋈ <sub>Order_elem.elem_id=Product_element.id</sub>
Product_element ⋈<sub>Product_element.product_id=Product.id</sub> Product))