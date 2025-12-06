# social/services/donation_target_service.py

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


class DonationTargetService:
    """
    Service pour gérer la cible d'un don (Mother, Child, Project)
    Compatible avec GenericForeignKey.
    """

    # ----------------------------------------------------
    # 1️⃣ Résolution de target_type → Classe Django
    # ----------------------------------------------------
    @staticmethod
    def resolve_model(target_type: str):
        """
        Convertit 'mother', 'child', 'project' → Classe Django
        """
        from about.models import Mother, Child
        from social.models import Project

        MODEL_MAP = {
            "mother": Mother,
            "child": Child,
            "project": Project,
        }

        if not target_type:
            return None
        return MODEL_MAP.get(target_type.lower().strip())

    # ----------------------------------------------------
    # 2️⃣ Résolution de (target_type, target_id) → objet réel
    # ----------------------------------------------------
    @staticmethod
    def resolve_instance(target_type: str, target_id: int):
        """
        Retourne l'objet réel, ex : ('mother', 5) → Mother(id=5)
        """
        model_class = DonationTargetService.resolve_model(target_type)
        if not model_class or not target_id:
            return None
        try:
            return model_class.objects.get(id=target_id)
        except ObjectDoesNotExist:
            return None

    # ----------------------------------------------------
    # 3️⃣ Assignation de la GenericForeignKey au don
    # ----------------------------------------------------
    @staticmethod
    def assign_gfk(donation):
        """
        Met à jour donation.target_content_type / target_object_id
        depuis donation.target_type et donation.target_id
        """
        if not donation.target_type or not donation.target_id:
            return donation  # pas de cible

        target_obj = DonationTargetService.resolve_instance(
            donation.target_type, donation.target_id
        )
        if not target_obj:
            return donation

        donation.target_content_type = ContentType.objects.get_for_model(target_obj.__class__)
        donation.target_object_id = target_obj.id
        donation.target = target_obj
        donation.save()
        return donation

    # ----------------------------------------------------
    # 4️⃣ Assignation depuis request POST ou GET
    # ----------------------------------------------------
    @staticmethod
    def assign_from_request(donation, request):
        """
        Extrait target_type / target_id depuis request et met à jour le don
        """
        target_type = request.POST.get("target_type") or request.GET.get("target_type")
        target_id = request.POST.get("target_id") or request.GET.get("target_id")

        if not target_type or not target_id:
            return donation

        donation.target_type = target_type
        donation.target_id = int(target_id)
        return DonationTargetService.assign_gfk(donation)
