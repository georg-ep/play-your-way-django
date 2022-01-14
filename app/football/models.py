from django.db import models

# Create your models here.
import uuid


class Team(models.Model):
    team_id = models.PositiveIntegerField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
    )
    venue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class SeasonInfo(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    gameweek = models.IntegerField(
        default=0,
    )

class Match(models.Model):
    match_id = models.PositiveIntegerField(
        primary_key=True,
    )
    date = models.DateTimeField()
    gameweek = models.PositiveIntegerField(
        default=0,
    )
    homeTeam = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_games",
    )
    status = models.CharField(
        max_length=255,
        default="",
        null=True,
        blank=True,
    )
    winner = models.CharField(
      max_length=255,
      default="",
      null=True,
      blank=True,
    )
    home_goals = models.PositiveIntegerField(
      default=None,
      blank=True,
      null=True,
    )
    away_goals = models.PositiveIntegerField(
      default=None,
      blank=True,
      null=True,
    )
    awayTeam = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_games",
    )

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.homeTeam} vs {self.awayTeam}"



class Player(models.Model):
    player_id = models.PositiveIntegerField(
        primary_key=True,
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
    )
    name = models.CharField(
        max_length=255,
    )
    position = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    shirtNumber = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    nationality = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name
