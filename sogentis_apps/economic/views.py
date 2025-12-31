# /economic/views.py
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dashboard.permissions import is_vendor, is_b2b_user, is_admin
from economic.permissions import is_verified_vendor, is_b2b_manager


def economic_home_view(request):
    """
    Page d'accueil du pôle économique.
    Hub public vers E-commerce, B2B, Formations, Services, Ressources et Support.
    """

    user = request.user
    is_authenticated = user.is_authenticated

    # -----------------------------
    # Détection des rôles
    # -----------------------------
    roles = {
        "vendor": is_vendor(user) if is_authenticated else False,
        "verified_vendor": is_verified_vendor(user) if is_authenticated else False,
        "b2b": is_b2b_user(user) if is_authenticated else False,
        "b2b_manager": is_b2b_manager(user) if is_authenticated else False,
        "staff": is_admin(user) if is_authenticated else False,
    }

    # -----------------------------
    # Sections économiques
    # -----------------------------
    sections = [
        {
            "key": "ecommerce",
            "title": _("E-commerce"),
            "description": _("Produits, marketplace et commandes en ligne."),
            "url": reverse("economic:ecommerce:index"),
            "icon": "bi-cart-check",
            "visible": True,
            "locked": False,
        },
        {
            "key": "formations",
            "title": _("Formations"),
            "description": _("Formations en ligne, parcours certifiants et apprentissage continu."),
            "url": reverse("economic:formations:index"),
            "icon": "bi-mortarboard",
            "visible": True,
            "locked": False,
        },
        {
            "key": "resources",
            "title": _("Ressources"),
            "description": _("Documents, guides et contenus téléchargeables."),
            "url": reverse("economic:resources:index"),
            "icon": "bi-journal-text",
            "visible": True,
            "locked": False,
        },
        {
            "key": "services",
            "title": _("Services"),
            "description": _("Services numériques, accompagnement et solutions sur mesure."),
            "url": reverse("economic:services:index"),
            "icon": "bi-gear-wide-connected",
            "visible": True,
            "locked": False,
        },
        {
            "key": "support",
            "title": _("Support & Assistance"),
            "description": _("FAQ, assistance client et support technique."),
            "url": reverse("economic:support:index"),
            "icon": "bi-life-preserver",
            "visible": True,
            "locked": False,
        },
        # -----------------------------
        # ESPACE B2B
        # -----------------------------
        {
            "key": "b2b",
            "title": _("Espace B2B"),
            "description": _("Solutions professionnelles, commandes en gros et partenariats."),
            "url": reverse("economic:b2b:index"),
            "icon": "bi-building",
            "visible": roles["b2b"] or roles["b2b_manager"] or roles["staff"],
            "locked": not (roles["b2b"] or roles["b2b_manager"] or roles["staff"]),
        },
        # -----------------------------
        # ESPACE VENDEUR 
        # -----------------------------
        {
            "key": "vendor",
            "title": _("Espace Vendeur"),
            "description": _("Gestion des produits et commandes."),
            "url": reverse("dashboard:vendor:home"),
            "icon": "bi-shop",
            "visible": roles["vendor"] or roles["verified_vendor"] or roles["staff"],
            "locked": not (roles["vendor"] or roles["verified_vendor"] or roles["staff"]),
        },
        
        
        {
            "key": "youtube",
            "title": _("YouTube (Soutenir)"),
            "description": _("Abonnez-vous et regardez nos vidéos pour soutenir nos actions sociales."),
            "url": "https://www.youtube.com/@Sogentis",
            "icon": "bi-youtube",
            "visible": True,
            "locked": False,
        },

    ]

    context = {
        "page_title": _("Pôle Économique"),
        "sections": sections,

        # ✅ AJOUT CRUCIAL
        "section_menu": "economic/partials/_economic_menu.html",
        
        # -----------------------------
        "YOUTUBE_CHANNEL_NAME": "SOGENTIS",
        "YOUTUBE_CHANNEL_URL": "https://www.youtube.com/@SOGENTIS",          # ✅ remplace par ton vrai handle si différent
        "YOUTUBE_VIDEOS_URL": "https://www.youtube.com/@SOGENTIS/videos",    # ✅ idem

        "YT_SUBSCRIBERS_LABEL": "—",
        "YT_VIEWS_LABEL": "—",
        "YT_VIDEOS_LABEL": "—",

    }

    return render(request, "economic/index.html", context)






# # /economic/views.py
# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from dashboard.permissions import is_vendor, is_b2b_user, is_admin
# from economic.permissions import is_verified_vendor, is_b2b_manager


# def economic_home_view(request):
#     """
#     Page d'accueil du pôle économique.
#     Hub public vers E-commerce, B2B, Formations, Services, Ressources et Support.
#     """

#     user = request.user
#     is_authenticated = user.is_authenticated

#     # -----------------------------
#     # Détection des rôles
#     # -----------------------------
#     roles = {
#         "vendor": is_vendor(user) if is_authenticated else False,
#         "verified_vendor": is_verified_vendor(user) if is_authenticated else False,
#         "b2b": is_b2b_user(user) if is_authenticated else False,
#         "b2b_manager": is_b2b_manager(user) if is_authenticated else False,
#         "staff": is_admin(user) if is_authenticated else False,
#     }

#     # -----------------------------
#     # Sections économiques
#     # -----------------------------
#     sections = [
#         {
#             "key": "ecommerce",
#             "title": _("E-commerce"),
#             "description": _("Produits, marketplace et commandes en ligne."),
#             "url": reverse("economic:ecommerce:index"),
#             "icon": "bi-cart-check",
#             "visible": True,
#             "locked": False,
#         },
#         {
#             "key": "formations",
#             "title": _("Formations"),
#             "description": _("Formations en ligne, parcours certifiants et apprentissage continu."),
#             "url": reverse("economic:formations:course"),
#             "icon": "bi-mortarboard",
#             "visible": True,
#             "locked": False,
#         },
#         {
#             "key": "resources",
#             "title": _("Ressources"),
#             "description": _("Documents, guides et contenus téléchargeables."),
#             "url": reverse("economic:resources:index"),
#             "icon": "bi-journal-text",
#             "visible": True,
#             "locked": False,
#         },
#         {
#             "key": "services",
#             "title": _("Services"),
#             "description": _("Services numériques, accompagnement et solutions sur mesure."),
#             "url": reverse("economic:services:index"),
#             "icon": "bi-gear-wide-connected",
#             "visible": True,
#             "locked": False,
#         },
#         {
#             "key": "support",
#             "title": _("Support & Assistance"),
#             "description": _("FAQ, assistance client et support technique."),
#             "url": reverse("economic:support:index"),
#             "icon": "bi-life-preserver",
#             "visible": True,
#             "locked": False,
#         },

#         # =====================================================
#         # ESPACE B2B
#         # =====================================================
#         {
#             "key": "b2b",
#             "title": _("Espace B2B"),
#             "description": _("Solutions professionnelles, commandes en gros et partenariats."),
#             "url": reverse("economic:b2b:index"),
#             "icon": "bi-building",
#             "visible": roles["b2b"] or roles["b2b_manager"] or roles["staff"],
#             "locked": not (roles["b2b"] or roles["b2b_manager"] or roles["staff"]),
#         },

#         # =====================================================
#         # ESPACE VENDEUR
#         # =====================================================
#         {
#             "key": "vendor",
#             "title": _("Espace Vendeur"),
#             "description": _("Gestion des produits et commandes."),
#             "url": reverse("dashboard:vendor:vendor_index"),
#             "icon": "bi-shop",
#             "visible": roles["vendor"] or roles["verified_vendor"] or roles["staff"],
#             "locked": not (roles["vendor"] or roles["verified_vendor"] or roles["staff"]),
#         },
#     ]

#     context = {
#         "page_title": _("Pôle Économique"),
#         "sections": sections,
#     }

#     return render(request, "economic/index.html", context)





# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from dashboard.permissions import is_vendor, is_b2b_user


# def economic_home_view(request):
#     """
#     Page d'accueil du pôle économique
#     Rôle : hub public vers E-commerce, B2B, Formations, Services, Ressources et Support
#     """
#     user = request.user
#     is_authenticated = user.is_authenticated
#     vendor = is_vendor(user) if is_authenticated else False
#     b2b = is_b2b_user(user) if is_authenticated else False
#     staff = user.is_staff if is_authenticated else False


#     sections = [
#         {
#             "key": "ecommerce",
#             "title": _("E-commerce"),
#             "description": _("Produits, marketplace et commandes en ligne."),
#             "url": reverse("economic:ecommerce:index"),
#             "icon": "bi-cart-check",
#             "visible": True,

#         },

#         {
#             "key": "formations",
#             "title": _("Formations"),
#             "description": _("Formations en ligne, parcours certifiants et apprentissage continu."),
#             "url": reverse("economic:formations:index"),
#             "icon": "bi-mortarboard",
#             "visible": True,
#         },
#         {
#             "key": "resources",
#             "title": _("Ressources"),
#             "description": _("Documents, guides et contenus téléchargeables."),
#             "url": reverse("economic:resources:index"),
#             "icon": "bi-journal-text",
#             "visible": True,
#         },
#         {
#             "key": "services",
#             "title": _("Services"),
#             "description": _("Services numériques, accompagnement et solutions sur mesure."),
#             "url": reverse("economic:services:index"),
#             "icon": "bi-gear-wide-connected",
#             "visible": True,
#         },
#         {
#             "key": "support",
#             "title": _("Support & Assistance"),
#             "description": _("FAQ, assistance client et support technique."),
#             "url": reverse("economic:support:index"),
#             "icon": "bi-life-preserver",
#             "visible": True,
#         },
        
#         # ---------- ESPACE B2B ----------

#         {
#             "key": "b2b",
#             "title": _("Espace B2B"),
#             "description": _("Solutions professionnelles, commandes en gros et partenariats."),
#             "url": reverse("economic:b2b:index"),
#             "icon": "bi-building",
#             "visible": b2b or staff,
#             "locked": not (b2b or staff),
#         },
        
#         # ---------- ESPACE VENDEUR ----------
        
#         {
#             "key": "vendor",
#             "title": _("Espace Vendeur"),
#             "description": _("Gestion des produits et commandes."),
#             "url": reverse("dashboard:index"),
#             "icon": "bi-shop",
#             "visible": vendor or staff,
#             "locked": not (vendor or staff),
#         },
#     ]

#     context = {
#         "page_title": _("Pôle Économique"),
#         "sections": sections,
#     }

#     return render(request, "economic/index.html", context)










# # /economic/views.py
# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _


# def economic_home_view(request):
#     """
#     Page d'accueil du pôle économique
#     Rôle : hub vers ecommerce, formations, services et B2B
#     """

#     sections = [
#         {
#             "title": _("E-Commerce"),
#             "description": _("Produits, marketplace et commandes en ligne."),
#             "url": reverse("economic:ecommerce:shop"),
#             "icon": "bi-cart",
#         },
#         {
#             "title": _("Formations"),
#             "description": _("Formations en ligne et certifications."),
#             "url": reverse("economic:formations:course"),
#             "icon": "bi-mortarboard",
#         },
#         {
#             "title": _("Services Numériques"),
#             "description": _("Solutions IT, maintenance et accompagnement."),
#             "url": reverse("economic:services:numerique"),
#             "icon": "bi-gear",
#         },
#         {
#             "title": _("Espace Professionnels"),
#             "description": _("Commandes en gros et espace B2B."),
#             "url": reverse("economic:b2b:dashboard"),
#             "icon": "bi-building",
#         },
#         {
#             "title": _("Centre de Resources"),
#             "description": _("Documentation."),
#             "url": reverse("economic:resources:resource"),
#             "icon": "bi-question-circle",
#         },
#         {
#             "title": _("FAQ & Assistance"),
#             "description": _("Consultez les questions fréquentes ou contactez notre support pour toute aide."),
#             "url": reverse("economic:support:support"),
#             "icon": "bi-question-circle",
#         },
#     ]

#     context = {
#         "page_title": _("Pôle Économique"),
#         "sections": sections,
#     }

#     return render(request, "economic/econ_home.html", context)





# # economic/views.py
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# def economic_home_view(request)
#     """
#     Page d'accueil du pôle économique
#     Rôle : hub vers ecommerce, formations, services et B2B
#     """
#     sections = [
#         {
#             "title": _("E-Commerce"),
#             "description": _("Produits, marketplace et commandes en ligne."),
#             "url": "economic_ecommerce:catalog",
#             "icon": "bi-cart",
#         },
#         {
#             "title": _("Formations"),
#             "description": _("Formations en ligne et certifications."),
#             "url": "economic:formations_home",
#             "icon": "bi-mortarboard",
#         },
#         {
#             "title": _("Services Numériques"),
#             "description": _("Solutions IT, maintenance et accompagnement."),
#             "url": "economic:services_home",
#             "icon": "bi-gear",
#         },
#         {
#             "title": _("Espace Professionnels"),
#             "description": _("Commandes en gros et espace B2B."),
#             "url": "economic:b2b_home",
#             "icon": "bi-building",
#         },
#     ]

#     context = {
#         "page_title": _("Pôle Économique"),
#         "sections": sections,
#         # ECONOMIC_ENABLED sera déjà injecté par ton context processor
#     }
#     return render(request, "economic/econ_home.html", context)





# #economic/views.py
# economic/views.py
# from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator
# from django.utils.translation import gettext_lazy as _

# from django.shortcuts import render, redirect, get_object_or_404
# from economic.ecommerce.models import Product, Category

# def econ_index(request):
#     return render(request, "economic/shop.html")

# def economic_home(request):
#     products = Product.objects.filter(is_active=True)[:6]
#     return render(request, 'economic/economic_home.html', {'products': products})

# def shop_view(request):

#     # ============================
#     # 1. FILTRES
#     # ============================
#     category_slug = request.GET.get("category")
#     search_query = request.GET.get("q", "")
#     sort = request.GET.get("sort", "")  # price_asc, price_desc, newest

#     products = Product.objects.filter(is_active=True)

#     # Filtrer par catégorie
#     if category_slug:
#         products = products.filter(category__slug=category_slug)

#     # Filtrer par recherche texte
#     if search_query:
#         products = products.filter(name__icontains=search_query)

#     # Tri
#     if sort == "price_asc":
#         products = products.order_by("price")
#     elif sort == "price_desc":
#         products = products.order_by("-price")
#     elif sort == "newest":
#         products = products.order_by("-created_at")

#     # ============================
#     # 2. PAGINATION
#     # ============================
#     paginator = Paginator(products, 12)  # 12 produits par page
#     page_number = request.GET.get("page")
#     products_page = paginator.get_page(page_number)

#     # ============================
#     # 3. CATÉGORIES POUR LE SIDEBAR / MENU
#     # ============================
#     categories = Category.objects.all().order_by("name")

#     context = {
#         "products": products_page,
#         "categories": categories,
#         "category_selected": category_slug,
#         "search_query": search_query,
#         "sort": sort,
#     }

#     return render(request, "economic/shop.html", context)

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('econ:cart_detail')

# def cart_detail(request):
#     cart = request.session.get('cart', {})
#     products = Product.objects.filter(id__in=cart.keys())
#     cart_items = []
#     total = 0
#     for p in products:
#         qty = cart.get(str(p.id), 0)
#         cart_items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
#         total += p.price * qty
#     return render(request, 'economic/cart_detail.html', {'cart_items': cart_items, 'total': total})



# def products_list(request):
#     category_slug = request.GET.get('category')
#     categories = Category.objects.all()
#     products = Product.objects.filter(is_active=True)
#     if category_slug:
#         products = products.filter(category__slug=category_slug)
#     context = {
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'economic/products_list.html', context)


# def product_detail_view(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     return render(request, "economic/product_detail.html", {"product": product})

# def buynow_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     # Exemple simple : rediriger vers le panier avec ajout
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('econ:cart_detail')

# def track_order_view(request):
#     code = request.GET.get('code')
#     order = None
#     if code:
#         # order = Order.objects.filter(tracking_code=code).first()
#         pass
#     return render(request, "economic/track_order.html", {"order": order, "code": code})







# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _


# def economic_home_view(request):
#     """
#     Page d'accueil du pôle économique
#     Rôle : hub vers ecommerce, formations, services et B2B
#     """
#     context = {
#         "page_title": _("Pôle Économique"),
#         "sections": [
#             {
#                 "title": _("E-Commerce"),
#                 "description": _("Produits, marketplace et commandes en ligne."),
#                 "url": "economic:ecommerce_home",
#                 "icon": "bi-cart",
#             },
#             {
#                 "title": _("Formations"),
#                 "description": _("Formations en ligne et certifications."),
#                 "url": "economic:formations_home",
#                 "icon": "bi-mortarboard",
#             },
#             {
#                 "title": _("Services Numériques"),
#                 "description": _("Solutions IT, maintenance et accompagnement."),
#                 "url": "economic:services_home",
#                 "icon": "bi-gear",
#             },
#             {
#                 "title": _("Espace Professionnels"),
#                 "description": _("Commandes en gros et espace B2B."),
#                 "url": "economic:b2b_home",
#                 "icon": "bi-building",
#             },
#         ],
#     }
#     return render(request, "economic/econ_home.html", context)
