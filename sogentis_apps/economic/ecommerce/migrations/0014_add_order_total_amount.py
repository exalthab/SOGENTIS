from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0013_alter_order_uuid"),
    ]

    operations = [
        # total_amount est déjà présent dans une migration précédente sur une DB neuve
        migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop),
    ]
