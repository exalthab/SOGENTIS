# about/views/about_index.py

from django.shortcuts import render
from about.models import (
    AboutSubsection,
    TeamMember,
    Child,
    Mother,
    Partner,
    HeroBlock,
    Organigram,
)


def about_index_view(request):
    """
    Vue principale de la page 'À propos'.
    Charge toutes les données nécessaires pour l'affichage.
    Compatible Parler (FR/EN), CKEditor5, et sections dynamiques.
    """

    # 🔹 Sous-sections (onglets)
    # active_translations() = récupère uniquement la langue utilisée dans la session
    subsections = (
        AboutSubsection.objects.active_translations()
        .filter(is_active=True)
        .order_by("order")
    )

    # 🔹 Hero banner
    hero = HeroBlock.objects.active_translations().first()

    # 🔹 Organigramme (1 seul)
    organigram = Organigram.objects.active_translations().first()

    # 🔹 Équipe (conseil + employés)
    team_members = (
        TeamMember.objects.active_translations().order_by("order")
    )

    # 🔹 Enfants bénéficiaires
    children = Child.objects.active_translations().all()

    # 🔹 Mamans bénéficiaires
    mothers = Mother.objects.active_translations().all()

    # 🔹 Partenaires
    partners = Partner.objects.active_translations().all()

    return render(
        request,
        "about/about_index.html",
        {
            "subsections": subsections,
            "team_members": team_members,
            "children": children,
            "mothers": mothers,
            "partners": partners,
            "hero": hero,
            "organigram": organigram,
        },
    )