# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str):
        if not order_id:
            raise ValueError("order_id cannot be empty.")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        if not order_id:
            raise ValueError("order_id cannot be empty.")
        if new_status not in ("pending", "processing", "shipped", "delivered", "cancelled"):
            raise ValueError(f"Invalid order status '{new_status}'.")

        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        updated_order = {**order, "status": new_status}
        self.storage.save_order(order_id, updated_order)

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        if not status:
            raise ValueError("status cannot be empty.")
        if status not in ("pending", "processing", "shipped", "delivered", "cancelled"):
            raise ValueError(f"Invalid order status '{status}'.")
        return [order for order in self.list_all_orders() if order["status"] == status]
