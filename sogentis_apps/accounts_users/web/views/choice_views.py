# # accounts_users/web/views/choice_views.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# def choice_view(request):
#     mode = (request.GET.get("mode") or "auth").strip().lower()
#     if mode not in ("auth", "register"):
#         mode = "auth"

#     page_title = _("Accéder à votre espace") if mode == "auth" else _("Créer un compte")

#     return render(
#         request,
#         "accounts_users/auth/choice.html",
#         {"page_title": page_title, "mode": mode},
#     )
