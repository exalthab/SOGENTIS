class UsersTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 👉 Tu peux ajouter ici du tracking, logs, sessions, etc.
        response = self.get_response(request)
        return response
