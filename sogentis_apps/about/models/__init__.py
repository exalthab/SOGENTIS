# about/models/__init__.py
from .team_member import TeamMember
from .child import Child
from .mother import Mother
from .partner import Partner
from .organigram import Organigram
from .about_subsection import AboutSubsection
from .hero import HeroBlock  # 👈 ton fichier s’appelle hero.py

__all__ = [
    "TeamMember",
    "Child",
    "Mother",
    "Partner",
    "Organigram",
    "AboutSubsection",
    "HeroBlock",
]
