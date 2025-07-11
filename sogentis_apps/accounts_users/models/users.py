# accounts_users/models/users.py

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from accounts_users.managers.custom_user_manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Adresse e-mail'), unique=True)
    username = models.CharField(_('Nom d’utilisateur'), max_length=150, unique=True)

    is_active = models.BooleanField(_('Actif'), default=False)
    is_staff = models.BooleanField(_('Membre de l’équipe'), default=False)
    is_superuser = models.BooleanField(_('Superutilisateur'), default=False)

    date_joined = models.DateTimeField(_('Date d’inscription'), default=timezone.now)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Mis à jour le'), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email




## accounts_users/models/users.py -> 01/07
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from accounts_users.managers.custom_user_manager import CustomUserManager


# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(_('email address'), unique=True)
#     username = models.CharField(_('username'), max_length=150, unique=True)

#     is_active = models.BooleanField(_('active'), default=False)
#     is_staff = models.BooleanField(_('staff status'), default=False)
#     is_superuser = models.BooleanField(_('superuser status'), default=False)

#     date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
#     created_at = models.DateTimeField(_('created at'), auto_now_add=True)
#     updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')

#     def __str__(self):
#         return self.email
