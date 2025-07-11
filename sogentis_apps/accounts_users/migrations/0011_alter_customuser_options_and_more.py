# Generated by Django 5.2.3 on 2025-07-02 17:14

import accounts_users.models.users_profile
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts_users", "0010_alter_customuser_is_active"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={
                "ordering": ["-date_joined"],
                "verbose_name": "Utilisateur",
                "verbose_name_plural": "Utilisateurs",
            },
        ),
        migrations.AlterModelOptions(
            name="membershiprole",
            options={
                "ordering": ["label"],
                "verbose_name": "Rôle d’adhésion",
                "verbose_name_plural": "Rôles d’adhésion",
            },
        ),
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "verbose_name": "Profil utilisateur",
                "verbose_name_plural": "Profils utilisateur",
            },
        ),
        migrations.AlterModelOptions(
            name="userrole",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Rôle administratif",
                "verbose_name_plural": "Rôles administratifs",
            },
        ),
        migrations.AlterModelOptions(
            name="usersettings",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Paramètre utilisateur",
                "verbose_name_plural": "Paramètres utilisateurs",
            },
        ),
        migrations.RemoveField(
            model_name="membershiprole",
            name="name",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="status",
        ),
        migrations.RemoveField(
            model_name="userrole",
            name="role",
        ),
        migrations.RemoveField(
            model_name="userrole",
            name="user",
        ),
        migrations.RemoveField(
            model_name="usersettings",
            name="notifications_enabled",
        ),
        migrations.AddField(
            model_name="membershiprole",
            name="code",
            field=models.CharField(
                choices=[
                    ("MEMBER", "Membre"),
                    ("VOLUNTEER", "Volontaire"),
                    ("SPONSOR", "Donateur"),
                    ("INSTITUTION", "Institution"),
                ],
                default="MEMBER",
                max_length=20,
                unique=True,
                verbose_name="Code interne",
            ),
        ),
        migrations.AddField(
            model_name="membershiprole",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Créé le",
            ),
        ),
        migrations.AddField(
            model_name="membershiprole",
            name="label",
            field=models.CharField(
                default="Membre", max_length=255, verbose_name="Libellé"
            ),
        ),
        migrations.AddField(
            model_name="membershiprole",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
        ),
        migrations.AddField(
            model_name="userrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("admin", "Administrateur"),
                    ("superuser", "Super-utilisateur"),
                    ("moderator", "Modérateur"),
                ],
                default="admin",
                max_length=50,
                unique=True,
                verbose_name="Code interne",
            ),
        ),
        migrations.AddField(
            model_name="userrole",
            name="label",
            field=models.CharField(
                default="Administrateur", max_length=100, verbose_name="Nom du rôle"
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Créé le",
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="dark_mode",
            field=models.BooleanField(default=False, verbose_name="Mode sombre activé"),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="receive_newsletter",
            field=models.BooleanField(
                default=True, verbose_name="Recevoir la newsletter"
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="date_joined",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Date d’inscription"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="Adresse e-mail"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(default=False, verbose_name="Actif"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_staff",
            field=models.BooleanField(default=False, verbose_name="Membre de l’équipe"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_superuser",
            field=models.BooleanField(default=False, verbose_name="Superutilisateur"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(
                max_length=150, unique=True, verbose_name="Nom d’utilisateur"
            ),
        ),
        migrations.AlterField(
            model_name="membershiprole",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="judicial_record",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=accounts_users.models.users_profile.judicial_record_upload_path,
                verbose_name="Casier judiciaire",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="membership_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounts_users.membershiprole",
                verbose_name="Rôle d’adhésion",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=accounts_users.models.users_profile.profile_picture_upload_path,
                verbose_name="Photo de profil",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounts_users.userrole",
                verbose_name="Rôle administratif",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="userprofile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Utilisateur",
            ),
        ),
        migrations.AlterField(
            model_name="userrole",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Créé le",
            ),
        ),
        migrations.AlterField(
            model_name="userrole",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Actif"),
        ),
        migrations.AlterField(
            model_name="userrole",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="language",
            field=models.CharField(
                choices=[("fr", "Français"), ("en", "Anglais")],
                default="fr",
                max_length=10,
                verbose_name="Langue préférée",
            ),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="settings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Utilisateur",
            ),
        ),
    ]
