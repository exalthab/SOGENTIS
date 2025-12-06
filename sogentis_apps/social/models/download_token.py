# social/models/download_token.py
from __future__ import annotations

from django.db import models, IntegrityError
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import secrets

DEFAULT_VALIDITY_HOURS = 24          # Durée de validité par défaut
TOKEN_BYTES = 32                     # Taille "entropie" du token
MAX_TOKEN_LENGTH = 64                # Longueur max du champ (token_urlsafe(32) ~ 43 chars)

class DownloadToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="download_tokens",
        verbose_name=_("Utilisateur"),
    )
    document = models.ForeignKey(
        "social.Publication",            # ou "Publication" si le modèle est dans la même app
        on_delete=models.CASCADE,
        related_name="download_tokens",
        verbose_name=_("Document"),
    )
    token = models.CharField(
        _("Code"),
        max_length=MAX_TOKEN_LENGTH,
        unique=True,
        help_text=_("Code unique envoyé par email pour autoriser le re-téléchargement."),
    )
    created_at = models.DateTimeField(_("Créé le"), default=timezone.now, editable=False)
    expires_at = models.DateTimeField(_("Expire le"), null=True, blank=True)
    used = models.BooleanField(_("Déjà utilisé ?"), default=False)

    class Meta:
        verbose_name = _("Jeton de téléchargement")
        verbose_name_plural = _("Jetons de téléchargement")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "document"]),
            models.Index(fields=["used"]),
            models.Index(fields=["expires_at"]),
        ]
        constraints = [
            # Optionnel : éviter plusieurs tokens actifs identiques user+document
            # (côté code on invalide les anciens si besoin — ici on n'impose pas)
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user_id}:{getattr(self.document, 'id', None)}:{self.token[:8]}..."

    # --- Helpers de validité -------------------------------------------------

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= timezone.now()

    def is_valid(self) -> bool:
        """Valide si non utilisé et non expiré."""
        return (not self.used) and (not self.is_expired)

    def remaining_seconds(self) -> int | None:
        """Secondes restantes avant expiration (None si pas d'expiration)."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - timezone.now()
        return max(int(delta.total_seconds()), 0)

    # --- Génération / fabrique ----------------------------------------------

    @staticmethod
    def _new_token_string() -> str:
        """
        Génère une chaîne URL-safe.
        token_urlsafe(TOKEN_BYTES) produit ~ 4/3*TOKEN_BYTES chars (≈ 43 pour 32).
        On tronque par sécurité si jamais > MAX_TOKEN_LENGTH (rare).
        """
        s = secrets.token_urlsafe(TOKEN_BYTES)
        return s[:MAX_TOKEN_LENGTH]

    @classmethod
    def generate(cls, user, document, validity_hours: int = DEFAULT_VALIDITY_HOURS) -> "DownloadToken":
        """
        Génère et enregistre un token unique. Retry si collision (très improbable).
        """
        expires = timezone.now() + timezone.timedelta(hours=validity_hours)
        for _ in range(3):  # 3 tentatives par prudence
            token_str = cls._new_token_string()
            try:
                return cls.objects.create(
                    user=user,
                    document=document,
                    token=token_str,
                    expires_at=expires,
                    used=False,
                )
            except IntegrityError:
                # Collision extrêmement rare sur le unique=True — on retente
                continue
        # Si on arrive ici, quelque chose cloche (ex: entropie réduite)
        raise IntegrityError("Impossible de générer un token unique après plusieurs tentatives.")

    # --- Actions utilitaires -------------------------------------------------

    def mark_used(self, save: bool = True) -> None:
        """Marque le token comme utilisé."""
        self.used = True
        if save:
            self.save(update_fields=["used"])

    def renew(self, validity_hours: int = DEFAULT_VALIDITY_HOURS, save: bool = True) -> None:
        """
        Prolonge la validité à partir de maintenant.
        """
        self.expires_at = timezone.now() + timezone.timedelta(hours=validity_hours)
        self.used = False
        if save:
            self.save(update_fields=["expires_at", "used"])
