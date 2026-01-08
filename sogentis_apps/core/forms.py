# core/forms.py
from __future__ import annotations

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage
from core.services.turnstile import is_turnstile_enabled, verify_turnstile
from core.services.hcaptcha import is_hcaptcha_enabled, verify_hcaptcha


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, label="", widget=forms.HiddenInput(attrs={"autocomplete": "off"}))

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 6}),
        }
        labels = {"name": _("Nom"), "email": _("Email"), "message": _("Message")}

    def _client_ip(self) -> str | None:
        if not self.request:
            return None
        xff = self.request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
        ip = (self.request.META.get("REMOTE_ADDR") or "").strip()
        return ip or None

    def clean_website(self):
        if (self.cleaned_data.get("website") or "").strip():
            raise forms.ValidationError(_("Requête invalide."))
        return ""

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        blocked = set(getattr(settings, "CONTACT_BLOCKED_EMAIL_DOMAINS", []) or [])
        domain = email.split("@")[-1] if "@" in email else ""
        if domain and domain in blocked:
            raise forms.ValidationError(_("Merci d’utiliser une adresse email valide (non temporaire)."))
        return email

    def _looks_suspicious(self) -> bool:
        msg = (self.data.get("message") or "").lower()
        links = msg.count("http://") + msg.count("https://") + msg.count("www.")
        if links >= 2:
            return True
        spam_words = ("seo", "backlink", "casino", "crypto", "loan", "viagra")
        return any(w in msg for w in spam_words)

    def _require_hcaptcha(self) -> bool:
        if not is_hcaptcha_enabled():
            return False
        mode = (getattr(settings, "CONTACT_HCAPTCHA_MODE", "fallback") or "fallback").lower()
        if mode == "off":
            return False
        if mode == "always":
            return True

        # fallback:
        need = bool(self.request and self.request.session.get("contact_need_hcaptcha", False))
        if self._looks_suspicious():
            need = True
        return need

    def clean(self):
        cleaned = super().clean()
        ip = self._client_ip()

        # Turnstile (toujours si activé)
        if is_turnstile_enabled():
            token = (self.data.get("cf-turnstile-response") or "").strip()
            ok, _ = verify_turnstile(token, remoteip=ip)
            if not ok:
                raise forms.ValidationError(
                    _("Vérification anti-spam (Turnstile) échouée. Merci de réessayer."),
                    code="turnstile_failed",
                )

        # hCaptcha (uniquement si requis)
        if self._require_hcaptcha():
            token = (self.data.get("h-captcha-response") or "").strip()
            ok, _ = verify_hcaptcha(token, remoteip=ip)
            if not ok:
                raise forms.ValidationError(
                    _("Vérification anti-spam (hCaptcha) échouée. Merci de réessayer."),
                    code="hcaptcha_failed",
                )

        return cleaned




# # /core/forms.py

# from django import forms

# from .models import ContactMessage


# class ContactForm(forms.Form):
#     name = forms.CharField(max_length=100, label="Nom")
#     email = forms.EmailField(label="Email")
#     message = forms.CharField(widget=forms.Textarea, label="Message")
