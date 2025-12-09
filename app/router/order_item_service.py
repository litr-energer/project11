from app.repositories.order_item_repository import OrderItemRepository
from app.services.service import BaseService
from app.models.order_items import OrderItemModel

class OrderItemService(BaseService[OrderItemModel]):
    def __init__(self, order_item_repository: OrderItemRepository):
        super().__init__(order_item_repository)
        self.order_item_repository = order_item_repository
    
    def get_order_items(self, order_id: int, skip: int = 0, limit: int = 100):
        return self.order_item_repository.get_by_order(order_id, skip, limit)
    
    def calculate_order_total(self, order_id: int) -> float:
        items = self.order_item_repository.get_by_order(order_id)
        total = sum(item.unit_price * item.quantity for item in items)
        return total