# Generated by Django 3.2.6 on 2022-02-23 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20211119_1800'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='surname',
            new_name='last_name',
        ),
    ]