from django.core.exceptions import ObjectDoesNotExist

from accounts_users.models.users_economic_profile import UserEconomicProfile 


def update_user_profile(user_or_profile, data, files=None):
    """
    Met à jour STRICTEMENT un UserProfile.

    ✔ Champs autorisés UNIQUEMENT :
    - Identité
    - Contact
    - Pays
    - Photo de profil

    ❌ PAS de social ici
    """

    # --------------------------------------------------
    # 1️⃣ Récupération ou création du profil
    # --------------------------------------------------
    if isinstance(user_or_profile, UserEconomicProfile):
        profile = user_or_profile
    else:
        try:
            profile = user_or_profile.UserEconomicProfile
        except ObjectDoesNotExist:
            profile = UserEconomicProfile.objects.create(user=user_or_profile)

    # --------------------------------------------------
    # 2️⃣ Champs AUTORISÉS (réels)
    # --------------------------------------------------
    allowed_fields = [
        # Identité
        "first_name",
        "last_name",
        "middle_names",
        "nickname",
        "date_of_birth",
        "place_of_birth",

        # Contact
        "phone",
        "profession",
        "function",

        # Pays (ISO alpha-2)
        "country_of_birth",
        "country_of_residence",

        # Adresse
        "city_of_residence",
        "address",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(profile, field, data[field])

    # --------------------------------------------------
    # 3️⃣ FICHIERS AUTORISÉS
    # --------------------------------------------------
    if files:
        if files.get("profile_picture"):
            profile.profile_picture = files["profile_picture"]

    # --------------------------------------------------
    # 4️⃣ Sauvegarde
    # --------------------------------------------------
    profile.save()
    return profile
