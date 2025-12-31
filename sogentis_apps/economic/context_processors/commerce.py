# economic/context_processors/commerce.py
def commerce_mode(request):
    return {
        "commerce_mode": request.session.get("commerce_mode", "B2C")
    }
