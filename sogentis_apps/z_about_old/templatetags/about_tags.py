#about/templatetags/about_tags.py
from django import template
from z_about_old.models.about_section import AboutSection
from z_about_old.models.team_member import TeamMember
from z_about_old.models.partner import Partner

register = template.Library()

# ================================
# 🔹 TAGS PERSONNALISÉS
# ================================

@register.simple_tag
def get_about_sections():
    """Retourne toutes les sections triées par ordre."""
    return AboutSection.objects.all().order_by("order")


@register.simple_tag
def get_team_members():
    """Retourne tous les membres de l'équipe triés par ordre."""
    return TeamMember.objects.all().order_by("order")


@register.simple_tag
def get_partners():
    """Retourne tous les partenaires triés par ordre."""
    return Partner.objects.all().order_by("order")


@register.simple_tag
def get_about_section(section_type):
    """Retourne une seule section par type."""
    try:
        return AboutSection.objects.get(section_type=section_type)
    except AboutSection.DoesNotExist:
        return None


# ================================
# 🔹 FILTRE POUR IDENTIFIER UNE SECTION
# ================================

@register.filter
def get_section_id(sections, section_type):
    """
    Retourne l’ID d’une section via son type.
    Usage :
        sections|get_section_id:"mission"
    """
    for section in sections:
        if section.section_type == section_type:
            return section.id
    return None


# ================================
# 🔹 FILTRE SÉCURISÉ POUR LES IMAGES
# ================================

@register.filter
def file_or_static(file_field, default_path):
    """
    Retourne file.url si dispo sinon fallback statique.
    """
    if file_field and hasattr(file_field, "url"):
        try:
            return file_field.url
        except ValueError:
            return default_path
    return default_path


# ================================
# 🔹 INCLUSION TAG : Section Card
# ================================

@register.inclusion_tag("about/components/section_card.html")
def section_card(item, section_type):
    return {
        "item": item,
        "section_type": section_type
    }






# # about/templatetags/about_tags.py
# from django import template
# from about.models.about_section import AboutSection
# from about.models.team_member import TeamMember
# from about.models.partner import Partner

# register = template.Library()


# # =============================
# # 🔹 TAGS PERSONNALISÉS
# # =============================

# @register.simple_tag
# def get_about_sections():
#     """
#     Retourne toutes les sections About, triées par ordre.
#     """
#     return AboutSection.objects.all().order_by("order")


# @register.simple_tag
# def get_team_members():
#     """
#     Retourne tous les membres de l'équipe triés par ordre.
#     """
#     return TeamMember.objects.all().order_by("order")


# @register.simple_tag
# def get_partners():
#     """
#     Retourne tous les partenaires triés par ordre.
#     """
#     return Partner.objects.all().order_by("order")


# @register.simple_tag
# def get_about_section(section_type):
#     """
#     Retourne une section About spécifique selon son type.
#     """
#     try:
#         return AboutSection.objects.get(section_type=section_type)
#     except AboutSection.DoesNotExist:
#         return None


# # 🔹 Nouveau filtre pour récupérer l'ID d'une section par type
# @register.filter
# def get_section_id(sections, section_type):
#     """
#     Retourne l'id de la section correspondant à section_type
#     Usage : sections|get_section_id:"mission"
#     """
#     for section in sections:
#         if section.section_type == section_type:
#             return section.id
#     return None


# # =============================
# # 🔹 FILTRE SÉCURISÉ POUR LES FICHIERS
# # =============================

# @register.filter
# def file_or_static(file_field, default_path):
#     """
#     Retourne l'URL d'un champ FileField/ImageField s'il existe,
#     sinon retourne le chemin statique fourni.
    
#     Exemple :
#         {{ member.photo|file_or_static:'/static/about/img/default_team.png' }}
#     """
#     if file_field and hasattr(file_field, "url"):
#         try:
#             return file_field.url
#         except ValueError:
#             # Si le fichier n'a pas d'URL associée (non uploadé)
#             return default_path
#     return default_path

# # =============================

# @register.inclusion_tag('about/components/section_card.html')
# def section_card(item, section_type):
#     return {'item': item, 'section_type': section_type}


# # about/templatetags/about_tags.py
# from django import template
# from about.models.about_section import AboutSection
# from about.models.team_member import TeamMember
# from about.models.partner import Partner

# register = template.Library()


# @register.simple_tag
# def get_about_sections():
#     """
#     Retourne toutes les sections About, triées par ordre
#     """
#     return AboutSection.objects.all().order_by("order")


# @register.simple_tag
# def get_team_members():
#     """
#     Retourne tous les membres de l'équipe triés par ordre
#     """
#     return TeamMember.objects.all().order_by("order")


# @register.simple_tag
# def get_partners():
#     """
#     Retourne tous les partenaires triés par ordre
#     """
#     return Partner.objects.all().order_by("order")


# @register.simple_tag
# def get_about_section(section_type):
#     """
#     Retourne une section About spécifique
#     """
#     try:
#         return AboutSection.objects.get(section_type=section_type)
#     except AboutSection.DoesNotExist:
#         return None


# # 🔹 Nouveau filtre pour récupérer l'ID d'une section par type
# @register.filter
# def get_section_id(sections, section_type):
#     """
#     Retourne l'id de la section correspondant à section_type
#     Usage : sections|get_section_id:"mission"
#     """
#     for section in sections:
#         if section.section_type == section_type:
#             return section.id
#     return None
