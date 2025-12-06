# about/templatetags/about_tags.py
from datetime import date
from django import template
from about.models import (
    AboutSubsection,
    TeamMember,
    Child,
    Mother,
    Partner,
    HeroBlock,
    Organigram,
)

register = template.Library()

# ============================================================
# 🔹 CALCUL D’ÂGE (ENFANTS) — UTILITAIRE (optionnel)
# ============================================================
def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


# ============================================================
# 🔹 ABOUT SUBSECTIONS (TABS)
#    Utilise la liste "subsections" envoyée par la vue
# ============================================================
@register.inclusion_tag(
    "about/components/about_subsection.html",
    takes_context=True,
)
def render_about_subsections(context):
    """
    Affiche les sous-sections (onglets) passées par la vue.
    Ne refait pas de requête ici.
    """
    subsections = context.get("subsections")
    return {
        "subsections": subsections,
        "request": context.get("request"),
    }


# ============================================================
# 🔹 HERO BANNER
# ============================================================
@register.inclusion_tag("about/components/hero.html")
def render_hero():
    return {"hero": HeroBlock.objects.first()}


# ============================================================
# 🔹 ORGANIGRAMME
# ============================================================
@register.inclusion_tag("about/components/organigram.html")
def render_organigram():
    return {"organigram": Organigram.objects.first()}


# ============================================================
# 🔹 TEAM MEMBERS
#    (tag peu utilisé : tu préfères boucler dans about_index.html)
# ============================================================
@register.inclusion_tag("about/components/team_member_card.html")
def render_team_members():
    """
    Inclusion tag laissé pour compatibilité éventuelle.
    Dans ta page About, tu boucles déjà sur `team_members` dans about_index.html
    et tu inclus team_member_card.html avec `{% with t=t %}...{% endwith %}`.
    """
    # Si un jour tu veux l’utiliser, adapte le template associé.
    board_members = TeamMember.objects.filter(category="board").order_by("order")
    employees = TeamMember.objects.filter(category="employee").order_by("order")
    return {
        "board_members": board_members,
        "employees": employees,
    }


# ============================================================
# 🔹 CHILDREN — retourne les objets Child natifs
# ============================================================
@register.inclusion_tag("about/components/child_card.html")
def render_child():
    """
    Renvoie directement les objets Child.
    Le template utilise donc : c.name, c.photo.url, c.age, etc.
    """
    children = Child.objects.all().prefetch_related("translations")
    return {"children": children}


# ============================================================
# 🔹 MOTHERS — retourne les objets Mother natifs
# ============================================================
@register.inclusion_tag("about/components/mother_card.html")
def render_mothers():
    """
    Renvoie directement les objets Mother.
    Le template utilise : m.name, m.photo.url, m.activity, etc.
    """
    mothers = Mother.objects.all().prefetch_related("translations")
    return {"mothers": mothers}


# ============================================================
# 🔹 PARTNERS
# ============================================================
@register.inclusion_tag("about/components/partner_card.html")
def render_partners():
    return {"partners": Partner.objects.all()}


# ============================================================
# 🔹 FILTRES UTILITAIRES
# ============================================================
@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, None)


@register.filter
def get_field(obj, field_name):
    return getattr(obj, field_name, "")


@register.filter
def translate(obj, field):
    """
    Retourne la valeur traduite depuis un objet Parler ou un dict.
    - Pour les modèles Parler : obj.safe_translation_getter(field)
    - Pour un dict (compat retro) : obj[field]
    """
    if obj is None:
        return ""

    # Cas 1 — dict déjà préparé ailleurs
    if isinstance(obj, dict):
        return obj.get(field, "")

    # Cas 2 — objet avec safe_translation_getter (Parler)
    getter = getattr(obj, "safe_translation_getter", None)
    if callable(getter):
        return getter(field, any_language=True)

    # Fallback
    return getattr(obj, field, "")


@register.filter
def split(value, delimiter):
    return value.split(delimiter)


@register.filter
def startswith(text, prefix):
    return str(text).startswith(str(prefix)) if text else False


@register.filter
def zip_lists(list1, list2):
    return zip(list1, list2)
