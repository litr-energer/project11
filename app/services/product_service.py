# app/services/product_service.py

from app.repositories.product_repository import ProductRepository
from app.services.service import BaseService
from app.models.products import ProductModel


class ProductService(BaseService[ProductModel]):
    def __init__(self, product_repository: ProductRepository):
        super().__init__(product_repository)
        self.product_repository = product_repository
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 100):
        return self.product_repository.get_by_category(category, skip, limit)
    
    def get_active_products(self, skip: int = 0, limit: int = 100):
        # ИСПРАВЛЕНО: is_acctive → is_active
        return self.product_repository.filter_by(is_active=True)