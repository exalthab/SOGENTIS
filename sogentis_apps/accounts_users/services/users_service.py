from django.contrib.auth import get_user_model

from accounts_users.models.users_economic_profile import UserEconomicProfile

User = get_user_model()


# --------------------------------------------------------------------
# 1️⃣ Création utilisateur + profil (VERSION PROPRE)
# --------------------------------------------------------------------
def create_user_with_profile(user_data, profile_data, files=None):
    """
    Crée un utilisateur + son profil utilisateur CENTRAL (plateforme / économique).
    ⚠️ N’écrit QUE les champs existants dans UserProfile.
    """

    # --------------------------------------------------
    # UTILISATEUR
    # --------------------------------------------------
    user = User.objects.create_user(
        email=user_data.get("email"),
        username=user_data.get("username") or user_data.get("email"),
        password=user_data.get("password"),
        is_active=False,
    )

    # --------------------------------------------------
    # PROFIL UTILISATEUR (CENTRAL)
    # --------------------------------------------------
    profile = UserEconomicProfile.objects.create(
        user=user,

        # Identité
        first_name=profile_data.get("first_name"),
        last_name=profile_data.get("last_name"),

        # Contact
        phone=profile_data.get("phone"),

        # Pays (ISO alpha-2 UNIQUEMENT)
        country_of_residence=profile_data.get("country_of_residence"),
        country_of_birth=profile_data.get("country_of_birth"),

        # Fichier autorisé ICI : photo uniquement
        profile_picture=files.get("profile_picture") if files else None,
    )

    return user, profile


# --------------------------------------------------------------------
# 2️⃣ Vérification rôle social (DÉPLACÉ LOGIQUEMENT)
# --------------------------------------------------------------------
def has_social_role(user) -> bool:
    """
    Vérifie si l'utilisateur a un profil social (ONG).
    """
    if not user.is_authenticated:
        return False

    return hasattr(user, "social_profile")







# # accounts_users/services/users_service.py 21/12/2025 error
# from django.contrib.auth import get_user_model

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole

# User = get_user_model()


# # --------------------------------------------------------------------
# # 1️⃣ Création utilisateur + profil (CORRIGÉ)
# # --------------------------------------------------------------------
# def create_user_with_profile(user_data, profile_data, files=None):
#     """
#     Crée un utilisateur + son profil associé.
#     ⚠️ Écrit UNIQUEMENT des champs existants
#     ⚠️ Respecte CountryField (ISO alpha-2)
#     """

#     user = User.objects.create_user(
#         email=user_data.get("email"),
#         username=user_data.get("username") or user_data.get("email"),
#         password=user_data.get("password"),
#         is_active=False,
#     )

#     # ---------- Rôle social ----------
#     role = None
#     role_id = profile_data.get("membership_role")

#     if isinstance(role_id, int):
#         role = MembershipRole.objects.filter(id=role_id).first()
#     elif isinstance(role_id, MembershipRole):
#         role = role_id

#     # ---------- PROFIL ----------
#     profile = UserProfile.objects.create(
#         user=user,

#         # Identité
#         first_name=profile_data.get("first_name"),
#         last_name=profile_data.get("last_name"),

#         # Contact
#         phone=profile_data.get("phone"),

#         # ⚠️ CountryField = ISO alpha-2 UNIQUEMENT
#         country_of_residence=profile_data.get("country_of_residence"),
#         country_of_birth=profile_data.get("country_of_birth"),

#         # Social
#         membership_role=role,

#         # Divers
#         message=profile_data.get("message"),

#         # Fichiers
#         profile_picture=files.get("profile_picture") if files else None,
#         judicial_record=files.get("judicial_record") if files else None,
#     )

#     return user, profile


# # --------------------------------------------------------------------
# # 2️⃣ Génération code social (CORRIGÉ)
# # --------------------------------------------------------------------
# def generate_membership_code(role_code: str) -> str:
#     prefix_map = {
#         "MEMBER": "M",
#         "SPONSOR": "D",
#         "VOLUNTEER": "V",
#         "INSTITUTION": "I",
#     }

#     prefix = prefix_map.get(role_code, "X")

#     last_profile = (
#         UserProfile.objects.filter(
#             membership_role__code=role_code,
#             social_registration_code__startswith=prefix,
#         )
#         .order_by("-social_registration_code")
#         .first()
#     )

#     last_number = (
#         int(last_profile.social_registration_code[1:])
#         if last_profile and last_profile.social_registration_code
#         else 0
#     )

#     return f"{prefix}{last_number + 1:03d}"


# # --------------------------------------------------------------------
# # 3️⃣ Rôle social (CORRIGÉ)
# # --------------------------------------------------------------------
# def has_social_role(user) -> bool:
#     """
#     Donateur, membre, volontaire, institution, etc.
#     """
#     if not user.is_authenticated:
#         return False

#     profile = getattr(user, "userprofile", None)
#     return bool(profile and profile.membership_role)








# # accounts_users/services/users_service.py Novembre 2025
# from django.contrib.auth import get_user_model
# from accounts_users.models.users_profile import UserProfile, MembershipRole

# User = get_user_model()


# # --------------------------------------------------------------------
# # 1️⃣ Création utilisateur + profil
# # --------------------------------------------------------------------
# def create_user_with_profile(user_data, profile_data, files=None):
#     """
#     Crée un utilisateur + son profil associé.
#     """

#     user = User.objects.create_user(
#         email=user_data.get("email"),
#         username=user_data.get("username") or user_data.get("email"),
#         password=user_data.get("password"),
#         is_active=False,
#     )

#     role = None
#     role_id = profile_data.get("membership_role")

#     if isinstance(role_id, int):
#         role = MembershipRole.objects.filter(id=role_id).first()
#     elif isinstance(role_id, MembershipRole):
#         role = role_id

#     profile = UserProfile.objects.create(
#         user=user,
#         full_name=profile_data.get("full_name"),
#         phone=profile_data.get("phone"),
#         country=profile_data.get("country"),
#         message=profile_data.get("message"),
#         membership_role=role,
#         profile_picture=files.get("profile_picture") if files else None,
#         judicial_record=files.get("judicial_record") if files else None,
#     )

#     return user, profile


# # --------------------------------------------------------------------
# # 2️⃣ Génération code d’adhésion
# # --------------------------------------------------------------------
# def generate_membership_code(role_code: str) -> str:
#     prefix_map = {
#         "MEMBER": "M",
#         "SPONSOR": "D",
#         "VOLUNTEER": "V",
#         "INSTITUTION": "I",
#     }

#     prefix = prefix_map.get(role_code, "X")

#     last_profile = (
#         UserProfile.objects.filter(
#             membership_role__code=role_code,
#             membership_code__startswith=prefix,
#         )
#         .order_by("-membership_code")
#         .first()
#     )

#     last_number = (
#         int(last_profile.membership_code[1:])
#         if last_profile and last_profile.membership_code
#         else 0
#     )

#     return f"{prefix}{last_number + 1:03d}"


# # --------------------------------------------------------------------
# # 3️⃣ Rôle social
# # --------------------------------------------------------------------
# def has_social_role(user) -> bool:
#     """
#     Donateur, membre, volontaire, institution, etc.
#     """
#     if not user.is_authenticated:
#         return False

#     profile = getattr(user, "profile", None)
#     return bool(profile and profile.membership_role)







# # accounts_users/views/users_service.py
# from django.contrib.auth import get_user_model
# from accounts_users.models.users_profile import UserProfile, MembershipRole

# User = get_user_model()


# # --------------------------------------------------------------------
# # 1️⃣ Création d’un utilisateur + profil associé
# # --------------------------------------------------------------------
# def create_user_with_profile(user_data, profile_data, files=None):
#     """
#     Crée un utilisateur + son profil associé.
#     - user_data : dict (email, username, password)
#     - profile_data : dict (full_name, phone, country, membership_role, message…)
#     - files : dict optionnel { profile_picture, judicial_record }
#     """

#     # --------------------------
#     # Création du USER
#     # --------------------------
#     user = User.objects.create_user(
#         email=user_data.get("email"),
#         username=user_data.get("username") or user_data.get("email"),
#         password=user_data.get("password"),
#         is_active=False,  # Activation obligatoire par e-mail
#     )

#     # --------------------------
#     # Gestion du rôle d’adhésion
#     # --------------------------
#     role = None
#     role_id = profile_data.get("membership_role")

#     if isinstance(role_id, int):
#         # Si un ID de rôle est passé → la FK fonctionne
#         try:
#             role = MembershipRole.objects.get(id=role_id)
#         except MembershipRole.DoesNotExist:
#             role = None
#     elif isinstance(role_id, MembershipRole):
#         # Si on a déjà un objet MembershipRole
#         role = role_id

#     # --------------------------
#     # Création du PROFIL utilisateur
#     # --------------------------
#     profile = UserProfile.objects.create(
#         user=user,
#         full_name=profile_data.get("full_name"),
#         phone=profile_data.get("phone"),
#         country=profile_data.get("country"),
#         message=profile_data.get("message"),
#         membership_role=role,
#         profile_picture=files.get("profile_picture") if files else None,
#         judicial_record=files.get("judicial_record") if files else None,
#     )

#     return user, profile


# # --------------------------------------------------------------------
# # 2️⃣ Génération du code d’adhésion
# # --------------------------------------------------------------------
# def generate_membership_code(role_code):
#     """
#     Génère un code unique d’adhésion :
#     - M001, M002… → MEMBER
#     - D001, D002… → SPONSOR
#     - V001, V002… → VOLUNTEER
#     - I001, I002… → INSTITUTION
#     """

#     prefix = {
#         "MEMBER": "M",
#         "SPONSOR": "D",
#         "VOLUNTEER": "V",
#         "INSTITUTION": "I",
#     }.get(role_code, "X")

#     # Récupère le dernier code existant pour ce rôle
#     last_profile = (
#         UserProfile.objects.filter(
#             membership_role__code=role_code,
#             membership_code__startswith=prefix,
#         )
#         .order_by("-membership_code")
#         .first()
#     )

#     # Numérotation
#     if last_profile and last_profile.membership_code:
#         # Ex : "M012" → 12
#         last_number = int(last_profile.membership_code[1:])
#     else:
#         last_number = 0

#     # Retourne ex : "M013"
#     return f"{prefix}{last_number + 1:03d}"

# def has_social_role(user):
#     """
#     Vérifie si l'utilisateur possède un rôle social
#     (donateur, membre, volontaire, institution, etc.)
#     """
#     if not user.is_authenticated:
#         return False

#     try:
#         profile = user.profile
#     except Exception:
#         return False

#     return profile.membership_role is not None
