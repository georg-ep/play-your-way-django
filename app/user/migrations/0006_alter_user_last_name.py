# Generated by Django 3.2.6 on 2022-02-23 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_user_is_onboarded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=64, null=True, verbose_name='Surname'),
        ),
    ]
