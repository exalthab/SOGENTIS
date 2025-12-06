# about/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import TeamMember, Partner, AboutSection
import logging

# Logger pour le suivi console
logger = logging.getLogger(__name__)

# Fonction utilitaire pour envoyer un mail à l'admin
def notify_admin(subject, message):
    admin_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not admin_email:
        logger.warning("[ABOUT] Aucun DEFAULT_FROM_EMAIL défini dans settings.py — email non envoyé.")
        return
    try:
        send_mail(
            subject,
            message,
            admin_email,
            [admin_email],  # l'admin reçoit le mail
            fail_silently=False,
        )
        logger.info(f"[ABOUT] Email envoyé à l’administrateur : {subject}")
    except Exception as e:
        logger.error(f"[ABOUT] Erreur lors de l’envoi de l’email : {e}")

# --- MEMBRES D'ÉQUIPE ---
@receiver(post_save, sender=TeamMember)
def team_member_saved(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[ABOUT] Nouveau membre ajouté : {instance.name} ({instance.role})")
        notify_admin(
            "👥 Nouveau membre d’équipe ajouté",
            f"Nom : {instance.name}\nRôle : {instance.role}\n\nCe membre a été ajouté à la page À propos."
        )
    else:
        logger.info(f"[ABOUT] Membre mis à jour : {instance.name} ({instance.role})")

@receiver(post_delete, sender=TeamMember)
def team_member_deleted(sender, instance, **kwargs):
    logger.warning(f"[ABOUT] Membre supprimé : {instance.name}")
    notify_admin(
        "⚠️ Membre supprimé",
        f"Le membre {instance.name} ({instance.role}) a été supprimé de la base de données."
    )

# --- PARTENAIRES ---
@receiver(post_save, sender=Partner)
def partner_saved(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[ABOUT] Nouveau partenaire ajouté : {instance.name}")
        notify_admin(
            "🤝 Nouveau partenaire ajouté",
            f"Nom : {instance.name}\nSite : {instance.website or 'Non précisé'}\n\nUn nouveau partenaire a été ajouté à la page À propos."
        )
    else:
        logger.info(f"[ABOUT] Partenaire mis à jour : {instance.name}")

@receiver(post_delete, sender=Partner)
def partner_deleted(sender, instance, **kwargs):
    logger.warning(f"[ABOUT] Partenaire supprimé : {instance.name}")
    notify_admin(
        "⚠️ Partenaire supprimé",
        f"Le partenaire {instance.name} a été supprimé de la base de données."
    )

# --- SECTIONS À PROPOS ---
@receiver(post_save, sender=AboutSection)
def about_section_saved(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[ABOUT] Nouvelle section créée : {instance.title} ({instance.section_type})")
    else:
        logger.info(f"[ABOUT] Section mise à jour : {instance.title} ({instance.section_type})")

@receiver(post_delete, sender=AboutSection)
def about_section_deleted(sender, instance, **kwargs):
    logger.warning(f"[ABOUT] Section supprimée : {instance.title} ({instance.section_type})")

@receiver(post_save, sender=Partner)
def partner_added(sender, instance, created, **kwargs):
    if created:
        print(f"✅ Nouveau partenaire ajouté : {instance.name}")


@receiver(post_save, sender=TeamMember)
def team_member_added(sender, instance, created, **kwargs):
    if created:
        print(f"👤 Nouveau membre d’équipe ajouté : {instance.name}")
