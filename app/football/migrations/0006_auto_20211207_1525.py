# Generated by Django 3.2.6 on 2021-12-07 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0005_alter_player_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='gameweek',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='match',
            name='awayTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_games', to='football.team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='homeTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_games', to='football.team'),
        ),
    ]
