# Generated by Django 3.2.6 on 2021-12-28 13:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0006_auto_20211207_1525'),
        ('bet', '0003_alter_bet_match'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bet',
            name='user1_accepted',
        ),
        migrations.RemoveField(
            model_name='bet',
            name='user2_accepted',
        ),
        migrations.AddField(
            model_name='bet',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='football.team'),
        ),
        migrations.CreateModel(
            name='BetScorer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('first_scorer', models.BooleanField(default=False)),
                ('bet_by_creator', models.BooleanField(default=True)),
                ('bet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bet.bet')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.player')),
            ],
        ),
    ]
