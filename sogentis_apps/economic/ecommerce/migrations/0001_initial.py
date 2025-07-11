# Generated by Django 5.2.3 on 2025-07-10 17:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name": "Catégorie",
                "verbose_name_plural": "Catégories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("price", models.PositiveIntegerField(verbose_name="Prix (XOF)")),
                ("description", models.TextField()),
                (
                    "fiche_technique",
                    models.TextField(
                        blank=True,
                        help_text="Fiche technique, caractéristiques (HTML ou Markdown accepté)",
                    ),
                ),
                ("image", models.ImageField(upload_to="economic/products/")),
                (
                    "is_new",
                    models.BooleanField(default=False, verbose_name="Nouveau produit"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Produit actif"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="ecommerce.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Produit",
                "verbose_name_plural": "Produits",
                "ordering": ["-created_at"],
            },
        ),
    ]
