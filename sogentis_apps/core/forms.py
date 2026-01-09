# core/forms.py
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from core.services.email_domain_check import is_email_domain_allowed


class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("Nom"),
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}),
    )

    def clean_email(self) -> str:
        email = (self.cleaned_data.get("email") or "").strip()
        ok, reason = is_email_domain_allowed(email)
        if not ok:
            raise forms.ValidationError(
                _("Adresse email refusée. Merci d’utiliser une adresse valide."),
                code=reason or "invalid-email-domain",
            )
        return email




# # core/forms.py
# from __future__ import annotations

# from django import forms
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .models import ContactMessage
# from core.services.turnstile import is_turnstile_enabled, verify_turnstile
# from core.services.hcaptcha import is_hcaptcha_enabled, verify_hcaptcha
# from core.services.antispam import domain_accepts_mail


# class ContactForm(forms.ModelForm):
#     website = forms.CharField(
#         required=False,
#         label="",
#         widget=forms.HiddenInput(attrs={"autocomplete": "off"})
#     )

#     def __init__(self, *args, request=None, **kwargs):
#         self.request = request
#         super().__init__(*args, **kwargs)

#     class Meta:
#         model = ContactMessage
#         fields = ("name", "email", "message")
#         widgets = {
#             "name": forms.TextInput(attrs={"autocomplete": "name"}),
#             "email": forms.EmailInput(attrs={"autocomplete": "email"}),
#             "message": forms.Textarea(attrs={"rows": 6}),
#         }
#         labels = {"name": _("Nom"), "email": _("Email"), "message": _("Message")}

#     def _client_ip(self) -> str | None:
#         if not self.request:
#             return None
#         xff = self.request.META.get("HTTP_X_FORWARDED_FOR", "")
#         if xff:
#             return xff.split(",")[0].strip()
#         ip = (self.request.META.get("REMOTE_ADDR") or "").strip()
#         return ip or None

#     def clean_website(self):
#         if (self.cleaned_data.get("website") or "").strip():
#             raise forms.ValidationError(_("Requête invalide."))
#         return ""

#     def clean_email(self):
#         raw_email = self.cleaned_data.get("email") or ""
#         if isinstance(raw_email, (list, tuple)):
#             raw_email = raw_email[0] if raw_email else ""
#         email = str(raw_email).strip().lower()

#         blocked = set(getattr(settings, "CONTACT_BLOCKED_EMAIL_DOMAINS", []) or [])
#         domain = email.split("@")[-1] if "@" in email else ""

#         if domain and domain in blocked:
#             raise forms.ValidationError(_("Merci d’utiliser une adresse email valide (non temporaire)."))

#         if domain and not domain_accepts_mail(domain):
#             raise forms.ValidationError(_("Domaine email invalide ou injoignable. Merci de vérifier votre adresse."))

#         return email

#     def _looks_suspicious(self) -> bool:
#         msg = (self.data.get("message") or "").lower()
#         links = msg.count("http://") + msg.count("https://") + msg.count("www.")
#         if links >= 2:
#             return True
#         spam_words = ("seo", "backlink", "casino", "crypto", "loan", "viagra")
#         return any(w in msg for w in spam_words)

#     def _require_hcaptcha(self) -> bool:
#         if not is_hcaptcha_enabled():
#             return False

#         mode = (getattr(settings, "CONTACT_HCAPTCHA_MODE", "fallback") or "fallback").lower()
#         if mode == "off":
#             return False
#         if mode == "always":
#             return True

#         need = bool(self.request and self.request.session.get("contact_need_hcaptcha", False))
#         if self._looks_suspicious():
#             need = True
#         return need

#     def clean(self):
#         cleaned = super().clean()

#         # ✅ Ne pas lancer captcha si champs requis invalides/vides
#         required_fields = ("name", "email", "message")
#         errors = getattr(self, "_errors", None) or {}
#         if any(field in errors for field in required_fields):
#             return cleaned
#         for f in required_fields:
#             v = cleaned.get(f)
#             if v is None or (isinstance(v, str) and not v.strip()):
#                 return cleaned

#         ip = self._client_ip()

#         # ✅ VRAI FALLBACK: si hCaptcha est requis et OK, on accepte sans forcer Turnstile
#         if self._require_hcaptcha():
#             token = (self.data.get("h-captcha-response") or "").strip()
#             ok, hc_errors = verify_hcaptcha(token, remoteip=ip)
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (hCaptcha) échouée. Merci de réessayer."),
#                     code="hcaptcha_failed",
#                 )
#             return cleaned

#         # Turnstile (si activé)
#         if is_turnstile_enabled():
#             token = (self.data.get("cf-turnstile-response") or "").strip()
#             ok, ts_errors = verify_turnstile(token, remoteip=ip)
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (Turnstile) échouée. Merci de réessayer."),
#                     code="turnstile_failed",
#                 )

#         return cleaned





# # core/forms.py
# from __future__ import annotations

# from django import forms
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .models import ContactMessage
# from core.services.turnstile import is_turnstile_enabled, verify_turnstile
# from core.services.hcaptcha import is_hcaptcha_enabled, verify_hcaptcha
# from core.services.email_domain_check import domain_accepts_mail


# class ContactForm(forms.ModelForm):
#     # Honeypot anti-bot (doit rester vide)
#     website = forms.CharField(
#         required=False,
#         label="",
#         widget=forms.HiddenInput(attrs={"autocomplete": "off"})
#     )

#     def __init__(self, *args, request=None, **kwargs):
#         self.request = request
#         super().__init__(*args, **kwargs)

#     class Meta:
#         model = ContactMessage
#         fields = ("name", "email", "message")
#         widgets = {
#             "name": forms.TextInput(attrs={"autocomplete": "name"}),
#             "email": forms.EmailInput(attrs={"autocomplete": "email"}),
#             "message": forms.Textarea(attrs={"rows": 6}),
#         }
#         labels = {
#             "name": _("Nom"),
#             "email": _("Email"),
#             "message": _("Message"),
#         }

#     # -----------------------------
#     # Helpers
#     # -----------------------------
#     def _client_ip(self) -> str | None:
#         if not self.request:
#             return None
#         xff = self.request.META.get("HTTP_X_FORWARDED_FOR", "")
#         if xff:
#             return xff.split(",")[0].strip()
#         ip = (self.request.META.get("REMOTE_ADDR") or "").strip()
#         return ip or None

#     def _looks_suspicious(self) -> bool:
#         msg = (self.data.get("message") or "").lower()
#         links = msg.count("http://") + msg.count("https://") + msg.count("www.")
#         if links >= 2:
#             return True
#         spam_words = ("seo", "backlink", "casino", "crypto", "loan", "viagra")
#         return any(w in msg for w in spam_words)

#     def _require_hcaptcha(self) -> bool:
#         """
#         Modes:
#           - off: jamais
#           - always: toujours
#           - fallback: seulement si session flag ou heuristique
#         """
#         if not is_hcaptcha_enabled():
#             return False

#         mode = (getattr(settings, "CONTACT_HCAPTCHA_MODE", "fallback") or "fallback").strip().lower()
#         if mode == "off":
#             return False
#         if mode == "always":
#             return True

#         # fallback
#         need = bool(self.request and self.request.session.get("contact_need_hcaptcha", False))
#         if self._looks_suspicious():
#             need = True
#         return need

#     # -----------------------------
#     # Field cleans
#     # -----------------------------
#     def clean_website(self):
#         if (self.cleaned_data.get("website") or "").strip():
#             raise forms.ValidationError(_("Requête invalide."))
#         return ""

#     def clean_email(self):
#         raw_email = self.cleaned_data.get("email") or ""
#         if isinstance(raw_email, (list, tuple)):
#             raw_email = raw_email[0] if raw_email else ""
#         email = str(raw_email).strip().lower()

#         blocked = set(getattr(settings, "CONTACT_BLOCKED_EMAIL_DOMAINS", []) or [])
#         domain = email.split("@")[-1] if "@" in email else ""

#         if domain and domain in blocked:
#             raise forms.ValidationError(_("Merci d’utiliser une adresse email valide (non temporaire)."))

#         # Vérification DNS (MX/A/AAAA)
#         if domain and not domain_accepts_mail(domain):
#             raise forms.ValidationError(_("Domaine email invalide ou injoignable. Merci de vérifier votre adresse."))

#         return email

#     # -----------------------------
#     # Form clean (captcha AFTER valid fields)
#     # -----------------------------
#     def clean(self):
#         cleaned = super().clean()

#         # ✅ IMPORTANT:
#         # Django appelle clean() même si des champs sont invalides/vides.
#         # On ne déclenche pas captcha si name/email/message ont déjà des erreurs.
#         required_fields = ("name", "email", "message")
#         errors = getattr(self, "_errors", None) or {}
#         if any(field in errors for field in required_fields):
#             return cleaned

#         # Si un champ requis est vide (sécurité UX), on skip captcha
#         for f in required_fields:
#             val = cleaned.get(f)
#             if val is None or (isinstance(val, str) and not val.strip()):
#                 return cleaned

#         ip = self._client_ip()

#         # Turnstile (si activé)
#         if is_turnstile_enabled():
#             token = (self.data.get("cf-turnstile-response") or "").strip()
#             ok, ts_errors = verify_turnstile(token, remoteip=ip)  # ✅ ne pas utiliser "_"
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (Turnstile) échouée. Merci de réessayer."),
#                     code="turnstile_failed",
#                 )

#         # hCaptcha (si requis)
#         if self._require_hcaptcha():
#             token = (self.data.get("h-captcha-response") or "").strip()
#             ok, hc_errors = verify_hcaptcha(token, remoteip=ip)  # ✅ ne pas utiliser "_"
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (hCaptcha) échouée. Merci de réessayer."),
#                     code="hcaptcha_failed",
#                 )

#         return cleaned





# # core/forms.py
# from __future__ import annotations

# from django import forms
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _

# from .models import ContactMessage
# from core.services.turnstile import is_turnstile_enabled, verify_turnstile
# from core.services.hcaptcha import is_hcaptcha_enabled, verify_hcaptcha

# from core.services.email_domain_check import domain_accepts_mail

# class ContactForm(forms.ModelForm):
#     website = forms.CharField(required=False, label="", widget=forms.HiddenInput(attrs={"autocomplete": "off"}))

#     def __init__(self, *args, request=None, **kwargs):
#         self.request = request
#         super().__init__(*args, **kwargs)

#     class Meta:
#         model = ContactMessage
#         fields = ("name", "email", "message")
#         widgets = {
#             "name": forms.TextInput(attrs={"autocomplete": "name"}),
#             "email": forms.EmailInput(attrs={"autocomplete": "email"}),
#             "message": forms.Textarea(attrs={"rows": 6}),
#         }
#         labels = {"name": _("Nom"), "email": _("Email"), "message": _("Message")}

#     def _client_ip(self) -> str | None:
#         if not self.request:
#             return None
#         xff = self.request.META.get("HTTP_X_FORWARDED_FOR", "")
#         if xff:
#             return xff.split(",")[0].strip()
#         ip = (self.request.META.get("REMOTE_ADDR") or "").strip()
#         return ip or None

#     def clean_website(self):
#         if (self.cleaned_data.get("website") or "").strip():
#             raise forms.ValidationError(_("Requête invalide."))
#         return ""

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()

#         blocked = set(getattr(settings, "CONTACT_BLOCKED_EMAIL_DOMAINS", []) or [])
#         domain = email.split("@")[-1] if "@" in email else ""

#         if domain and domain in blocked:
#             raise forms.ValidationError(_("Merci d’utiliser une adresse email valide (non temporaire)."))

#         # ✅ NOUVEAU: domaine doit exister et accepter le mail
#         if domain and not domain_accepts_mail(domain):
#             raise forms.ValidationError(_("Domaine email invalide ou injoignable. Merci de vérifier votre adresse."))

#         return email

#     def _looks_suspicious(self) -> bool:
#         msg = (self.data.get("message") or "").lower()
#         links = msg.count("http://") + msg.count("https://") + msg.count("www.")
#         if links >= 2:
#             return True
#         spam_words = ("seo", "backlink", "casino", "crypto", "loan", "viagra")
#         return any(w in msg for w in spam_words)

#     def _require_hcaptcha(self) -> bool:
#         if not is_hcaptcha_enabled():
#             return False
#         mode = (getattr(settings, "CONTACT_HCAPTCHA_MODE", "fallback") or "fallback").lower()
#         if mode == "off":
#             return False
#         if mode == "always":
#             return True

#         # fallback:
#         need = bool(self.request and self.request.session.get("contact_need_hcaptcha", False))
#         if self._looks_suspicious():
#             need = True
#         return need

#     def clean(self):
#         cleaned = super().clean()
#         ip = self._client_ip()

#         # Turnstile (toujours si activé)
#         if is_turnstile_enabled():
#             token = (self.data.get("cf-turnstile-response") or "").strip()
#             ok, _ = verify_turnstile(token, remoteip=ip)
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (Turnstile) échouée. Merci de réessayer."),
#                     code="turnstile_failed",
#                 )

#         # hCaptcha (uniquement si requis)
#         if self._require_hcaptcha():
#             token = (self.data.get("h-captcha-response") or "").strip()
#             ok, _ = verify_hcaptcha(token, remoteip=ip)
#             if not ok:
#                 raise forms.ValidationError(
#                     _("Vérification anti-spam (hCaptcha) échouée. Merci de réessayer."),
#                     code="hcaptcha_failed",
#                 )

#         return cleaned




# # /core/forms.py

# from django import forms

# from .models import ContactMessage


# class ContactForm(forms.Form):
#     name = forms.CharField(max_length=100, label="Nom")
#     email = forms.EmailField(label="Email")
#     message = forms.CharField(widget=forms.Textarea, label="Message")
