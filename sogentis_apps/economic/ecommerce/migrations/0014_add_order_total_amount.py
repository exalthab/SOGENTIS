from decimal import Decimal
from django.db import migrations, models


def backfill_total_amount(apps, schema_editor):
    Order = apps.get_model("ecommerce", "Order")
    db_alias = schema_editor.connection.alias

    # Sur ta DB prod, la colonne existante est "total" (int).
    # On copie total -> total_amount pour conserver les données.
    qs = Order.objects.using(db_alias).filter(total_amount__isnull=True).only("id")
    for o in qs.iterator(chunk_size=500):
        # getattr(..., 0) au cas où l'objet n'a pas 'total' côté modèle
        total = getattr(o, "total", 0) or 0
        Order.objects.using(db_alias).filter(id=o.id, total_amount__isnull=True).update(
            total_amount=Decimal(total)
        )


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0013_alter_order_uuid"),
    ]

    operations = [
        # 1) Ajout colonne nullable (safe)
        migrations.AddField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True),
        ),
        # 2) Backfill depuis "total"
        migrations.RunPython(backfill_total_amount, reverse_code=migrations.RunPython.noop),
        # 3) Verrouillage NOT NULL + default
        migrations.AlterField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00")),
        ),
    ]
