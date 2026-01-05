from django.db import migrations, connection


def create_vendor_table(apps, schema_editor):
    table = "ecommerce_vendor"
    with connection.cursor() as c:
        c.execute("SELECT to_regclass(%s)", [f"public.{table}"])
        exists = c.fetchone()[0] is not None
    if exists:
        return

    Vendor = apps.get_model("ecommerce", "Vendor")
    schema_editor.create_model(Vendor)


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0010_rename_paymenttransactions_paymenttransaction_and_more"),
    ]

    operations = [
        migrations.RunPython(create_vendor_table, migrations.RunPython.noop),
    ]
