# Generated by Django 3.1 on 2019-09-22 21:38

from django.db import migrations, models

from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):

    dependencies = [
        ("bad_flow_change_char_type_that_unsafe_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testtable",
            name="field",
            field=models.CharField(max_length=100),
        ),
    ]