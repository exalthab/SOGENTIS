from economic.support.models import FAQ


def get_active_faqs():
    return (
        FAQ.objects.select_related("category")
        .filter(is_active=True, category__is_active=True)
        .order_by("sort_order", "question")
    )
