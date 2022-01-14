from django.contrib import admin

from .models import Bet, BetScorer

# Register your models here.


@admin.register(BetScorer)
class BetScorerAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "first_scorer", "bet_by_creator", "bet", "player"]

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "match", "is_draw", "winner", "user1", "user2", "is_accepted", "amount"]

