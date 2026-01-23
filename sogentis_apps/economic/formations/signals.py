# economic/formations/signals.py
from __future__ import annotations

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from economic.formations.models import Enrollment


def _is_completed(enrollment: Enrollment) -> bool:
    """
    Enrollment terminé si:
    - status == COMPLETED
    - ou legacy completed=True
    """
    return (getattr(enrollment, "status", None) == Enrollment.Status.COMPLETED) or bool(getattr(enrollment, "completed", False))


@receiver(pre_save, sender=Enrollment)
def _enrollment_cache_old_completed(sender, instance: Enrollment, **kwargs):
    """
    Cache l'état "completed" avant modification pour savoir si on doit déclencher le certificat.
    """
    if not instance.pk:
        instance._old_completed_state = False
        return

    old = Enrollment.objects.filter(pk=instance.pk).values("status", "completed").first()
    if not old:
        instance._old_completed_state = False
        return

    instance._old_completed_state = (old.get("status") == Enrollment.Status.COMPLETED) or bool(old.get("completed"))


@receiver(post_save, sender=Enrollment)
def _enrollment_issue_certificate(sender, instance: Enrollment, created: bool, **kwargs):
    """
    Déclenche l'émission du certificat au passage vers COMPLETED.
    """
    now_completed = _is_completed(instance)
    old_completed = getattr(instance, "_old_completed_state", False)

    if not now_completed:
        return

    # déclencher seulement au passage vers COMPLETED (ou création déjà complétée)
    if not (created or not old_completed):
        return

    def _do():
        try:
            from economic.formations.services.certificate_service import issue_certificate_for_enrollment
            issue_certificate_for_enrollment(instance, generate_pdf=True, send_email=True)
        except Exception:
            # on évite de casser la transaction / save
            return

    transaction.on_commit(_do)





# # economic/formations/signals.py
# from __future__ import annotations

# from django.db import transaction
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver

# from economic.formations.models import Enrollment
# from economic.formations.services.certificates import generate_certificate


# # ---------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------
# def _is_completed(enrollment: Enrollment) -> bool:
#     """
#     Vérifie si l'enrollment est considéré comme terminé.
#     """
#     return (getattr(enrollment, "status", None) == Enrollment.Status.COMPLETED) \
#            or bool(getattr(enrollment, "completed", False))


# # ---------------------------------------------------------------------
# # Signals
# # ---------------------------------------------------------------------
# @receiver(pre_save, sender=Enrollment)
# def _enrollment_cache_old_completed(sender, instance: Enrollment, **kwargs):
#     """
#     Cache l'état "completed" avant modification pour savoir si on doit déclencher le certificat.
#     """
#     if not instance.pk:
#         instance._old_completed_state = False
#         return

#     old = Enrollment.objects.filter(pk=instance.pk).values("status", "completed").first()
#     if not old:
#         instance._old_completed_state = False
#         return

#     instance._old_completed_state = (old.get("status") == Enrollment.Status.COMPLETED) \
#                                     or bool(old.get("completed"))


# @receiver(post_save, sender=Enrollment)
# def _enrollment_issue_certificate(sender, instance: Enrollment, created: bool, **kwargs):
#     """
#     Déclenche l'émission du certificat si l'enrollment vient d'être complété.
#     """
#     now_completed = _is_completed(instance)
#     old_completed = getattr(instance, "_old_completed_state", False)

#     # déclencher seulement au passage vers COMPLETED (ou création déjà complétée)
#     if now_completed and (created or not old_completed):
#         def _do():
#             generate_certificate(instance, generate_pdf=True, send_email=True)

#         transaction.on_commit(_do)





# # # economic/formations/signals.py

# from __future__ import annotations

# from django.db import transaction
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver

# from economic.formations.models import Enrollment
# from economic.formations.services.certificates import issue_certificate_for_enrollment
# from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
# from economic.formations.services.certificate_email import send_certificate_email
# from economic.formations.services.certificates import generate_certificate


# # ---------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------
# def _is_completed(enrollment: Enrollment) -> bool:
#     """
#     Vérifie si l'enrollment est considéré comme terminé.
#     """
#     return (getattr(enrollment, "status", None) == Enrollment.Status.COMPLETED) or bool(getattr(enrollment, "completed", False))


# # ---------------------------------------------------------------------
# # Signals
# # ---------------------------------------------------------------------
# @receiver(pre_save, sender=Enrollment)
# def _enrollment_cache_old_completed(sender, instance: Enrollment, **kwargs):
#     """
#     Cache l'état "completed" avant modification pour savoir si on doit déclencher le certificat.
#     """
#     if not instance.pk:
#         instance._old_completed_state = False
#         return

#     old = Enrollment.objects.filter(pk=instance.pk).values("status", "completed").first()
#     if not old:
#         instance._old_completed_state = False
#         return

#     instance._old_completed_state = (old.get("status") == Enrollment.Status.COMPLETED) or bool(old.get("completed"))


# @receiver(post_save, sender=Enrollment)
# def _enrollment_issue_certificate(sender, instance: Enrollment, created: bool, **kwargs):
#     """
#     Déclenche l'émission du certificat si l'enrollment vient d'être complété.
#     """
#     now_completed = _is_completed(instance)
#     old_completed = getattr(instance, "_old_completed_state", False)

#     # déclencher seulement au passage vers COMPLETED (ou création déjà complétée)
#     if now_completed and (created or not old_completed):
#         def _do():
#             # Option 1 : utiliser le service moderne tout-en-un
#             generate_certificate(instance, generate_pdf=True, send_email=True)

#             # Option 2 : pour compatibilité legacy (PDF + email séparés)
#             # cert = issue_certificate_for_enrollment(instance)
#             # generate_certificate_pdf_and_attach(cert)
#             # send_certificate_email(cert)

#         transaction.on_commit(_do)






# # economic/formations/signals.py
# from django.db import transaction
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver

# from .models import Enrollment
# from .services.certificates import issue_certificate_for_enrollment
# from .services.certificate_pdf import generate_certificate_pdf_and_attach
# from .services.certificate_email import send_certificate_email


# @receiver(pre_save, sender=Enrollment)
# def _enrollment_cache_old_status(sender, instance: Enrollment, **kwargs):
#     if not instance.pk:
#         instance._old_status = None
#         return
#     instance._old_status = Enrollment.objects.filter(pk=instance.pk).values_list("status", flat=True).first()


# @receiver(post_save, sender=Enrollment)
# def _enrollment_issue_certificate(sender, instance: Enrollment, created: bool, **kwargs):
#     old = getattr(instance, "_old_status", None)
#     is_completed = instance.status == Enrollment.Status.COMPLETED or instance.completed

#     if is_completed and old != Enrollment.Status.COMPLETED:
#         def _do():
#             cert = issue_certificate_for_enrollment(instance)
#             generate_certificate_pdf_and_attach(cert)   # crée pdf si absent
#             send_certificate_email(cert)                # email + pdf
#         transaction.on_commit(_do)
