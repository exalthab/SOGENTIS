# Generated by Django 5.2.3 on 2025-07-09 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0010_alter_project_options_remove_project_goal_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="documentpurchase",
            options={
                "ordering": ["-purchased_at"],
                "verbose_name": "Achat de document",
                "verbose_name_plural": "Achats de documents",
            },
        ),
        migrations.AlterField(
            model_name="documentpurchase",
            name="has_downloaded",
            field=models.BooleanField(
                default=False,
                help_text="Empêche le téléchargement multiple. Si True, une demande manuelle est requise.",
                verbose_name="Déjà téléchargé ?",
            ),
        ),
    ]
