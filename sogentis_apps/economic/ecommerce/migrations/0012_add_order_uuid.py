from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0011_create_vendor_if_missing"),
    ]

    operations = [
        # champ uuid déjà présent via une migration précédente (ex: 0001_initial / hotfix)
        migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop),
    ]
