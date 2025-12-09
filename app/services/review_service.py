from app.repositories.review_repository import ReviewRepository
from app.services.service import BaseService
from app.models.review import ReviewModel

class ReviewService(BaseService[ReviewModel]):
    def __init__(self, review_repository: ReviewRepository):
        super().__init__(review_repository)
        self.review_repository = review_repository
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.review_repository.get_by_user(user_id, skip, limit)
    
    def get_by_product(self, product_id: int, skip: int = 0, limit: int = 100):
        return self.review_repository.get_by_product(product_id, skip, limit)
    
    def get_by_rating_range(self, min_rating: int = 1, max_rating: int = 5, skip: int = 0, limit: int = 100):
        return self.review_repository.get_by_rating(min_rating, max_rating, skip, limit)
    
    def get_verified_reviews(self, skip: int = 0, limit: int = 100):
        return self.review_repository.filter_by(is_verified=True)
    
    def calculate_average_rating(self, **filters) -> float:
        reviews = self.review_repository.filter_by(**filters)
        if not reviews:
            return 0.0
        
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)