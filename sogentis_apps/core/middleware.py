# core/middleware.py (ou economic/middleware.py)
class EcommerceSessionDefaultsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        s = request.session
        if "ECOMMERCE_COUNTRY" not in s:
            s["ECOMMERCE_COUNTRY"] = "SN"
        if "ECOMMERCE_CURRENCY" not in s:
            s["ECOMMERCE_CURRENCY"] = "XOF"
        return self.get_response(request)
# A voir si ce fichier doit être dans core ou economic
# Ou a etre suprimé si pas utilisé