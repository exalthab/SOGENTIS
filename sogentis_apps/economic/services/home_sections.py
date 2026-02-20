# economic/services/home_sections.py  (rappel: liens hub)
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_vendor, is_b2b_user, is_admin
from economic.permissions import is_verified_vendor, is_b2b_manager
from economic.utils.urls import safe_reverse


@dataclass(frozen=True)
class HomeLink:
    key: str
    title: str
    description: str
    url: str
    icon: str
    visible: bool = True
    locked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "icon": self.icon,
            "visible": self.visible,
            "locked": self.locked,
        }


def build_economic_home_sections(user) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    is_authenticated = bool(getattr(user, "is_authenticated", False))

    roles = {
        "vendor": is_vendor(user) if is_authenticated else False,
        "verified_vendor": is_verified_vendor(user) if is_authenticated else False,
        "b2b": is_b2b_user(user) if is_authenticated else False,
        "b2b_manager": is_b2b_manager(user) if is_authenticated else False,
        "staff": is_admin(user) if is_authenticated else False,
    }

    can_b2b = roles["b2b"] or roles["b2b_manager"] or roles["staff"]
    can_vendor = roles["vendor"] or roles["verified_vendor"] or roles["staff"]

    youtube_handle = "SOGENTIS"
    youtube_channel_url = f"https://www.youtube.com/@{youtube_handle}"
    youtube_videos_url = f"{youtube_channel_url}/videos"

    items: list[HomeLink] = [
        HomeLink("ecommerce", _("E-commerce"), _("Produits, marketplace et commandes en ligne."), safe_reverse("economic:ecommerce:index"), "bi-cart-check"),
        HomeLink("formations", _("Formations"), _("Formations en ligne, parcours certifiants et apprentissage continu."), safe_reverse("economic:formations:index"), "bi-mortarboard"),
        HomeLink("resources", _("Ressources"), _("Documents, guides et contenus téléchargeables."), safe_reverse("economic:resources:index"), "bi-journal-text"),
        HomeLink("prestations", _("Prestations"), _("Services numériques, accompagnement et solutions sur mesure."), safe_reverse("economic:prestations:index"), "bi-gear-wide-connected"),
        HomeLink("support", _("Support & Assistance"), _("FAQ, assistance client et support technique."), safe_reverse("economic:support:index"), "bi-life-preserver"),
        HomeLink("b2b", _("Espace B2B"), _("Solutions professionnelles, commandes en gros et partenariats."), safe_reverse("economic:b2b:index"), "bi-building", locked=not can_b2b),
        HomeLink("vendor", _("Espace Vendeur"), _("Gestion des produits et commandes."), safe_reverse("dashboard:vendor:home"), "bi-shop", locked=not can_vendor),
        HomeLink("youtube", _("YouTube (Soutenir)"), _("Abonnez-vous et regardez nos vidéos pour soutenir nos actions sociales."), youtube_channel_url, "bi-youtube"),
    ]

    extras = {
        "YOUTUBE_CHANNEL_NAME": youtube_handle,
        "YOUTUBE_CHANNEL_URL": youtube_channel_url,
        "YOUTUBE_VIDEOS_URL": youtube_videos_url,
        "YT_SUBSCRIBERS_LABEL": "—",
        "YT_VIEWS_LABEL": "—",
        "YT_VIDEOS_LABEL": "—",
        "roles": roles,
    }
    return [i.as_dict() for i in items], extras
