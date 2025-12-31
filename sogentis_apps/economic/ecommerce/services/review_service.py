# economic/ecommerce/services/review_service.py
from ..models.review import Review


def create_review(user, product, rating, title, content):
    return Review.objects.create(
        user=user,
        product=product,
        rating=rating,
        title=title,
        content=content,
        is_approved=False,  # modération admin
    )
