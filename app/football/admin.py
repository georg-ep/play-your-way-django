from django.contrib import admin
from .models import Team, Match, Player, SeasonInfo
from user.models import User

# Register your models here.

admin.site.register(Team)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["__str__", "gameweek", "date", "status"]
    # readonly_fields = ["score", "homeTeam", "awayTeam", "match_id", "gameweek", "status"]


@admin.register(SeasonInfo)
class SeasonInfoAdmin(admin.ModelAdmin):
    readonly_fields = ["gameweek"]


admin.site.register(Player)
admin.site.register(User)
