from app.repositories.order_repository import OrderRepository
from app.services.service import BaseService
from app.models.orders import OrderModel

class OrderService(BaseService[OrderModel]):
    def __init__(self, order_repository: OrderRepository):
        super().__init__(order_repository)
        self.order_repository = order_repository
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.order_repository.get_by_user(user_id, skip, limit)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        return self.order_repository.get_by_status(status, skip, limit)
    
    def update_status(self, order_id: int, status: str) -> OrderModel:
        return self.order_repository.update(order_id, {"status": status})