import uuid
from django.db import migrations, models


def backfill_order_uuid(apps, schema_editor):
    Order = apps.get_model("ecommerce", "Order")
    db_alias = schema_editor.connection.alias

    qs = Order.objects.using(db_alias).filter(uuid__isnull=True).only("id")
    for o in qs.iterator(chunk_size=500):
        Order.objects.using(db_alias).filter(id=o.id, uuid__isnull=True).update(uuid=uuid.uuid4())


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0011_create_vendor_if_missing"),
    ]

    operations = [
        # 1) on ajoute la colonne en NULL d'abord (safe)
        migrations.AddField(
            model_name="order",
            name="uuid",
            field=models.UUIDField(null=True, editable=False, db_index=True),
        ),

        # 2) backfill des lignes existantes
        migrations.RunPython(backfill_order_uuid, reverse_code=migrations.RunPython.noop),

        # 3) on verrouille comme attendu par le code
        migrations.AlterField(
            model_name="order",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        
        
    ]
