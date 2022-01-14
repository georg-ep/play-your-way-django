from django.db import models
import uuid
from football.models import Match, Team, Player

from user.models import User

# Create your models here.


class Bet(models.Model):
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
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
    )
    is_draw = models.BooleanField(
        default=False,
    )
    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="creator",
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="opponent",
    )
    is_accepted = models.BooleanField(
        default=False,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
    )

    def __str__(self):
        prefix = "open:"
        if self.is_accepted:
            prefix = "confirmed:"
        return prefix + str(self.uid)


class BetScorer(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    first_scorer = models.BooleanField(
        default=False,
    )
    bet_by_creator = models.BooleanField(
        default=True,
    )
    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE,
        related_name="scorers",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.player.name} to score"
