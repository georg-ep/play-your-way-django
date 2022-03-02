from django.contrib import admin
from .models import Team, Match, Player, SeasonInfo
from user.models import User, Clients

# Register your models here.

admin.site.register(Team)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["__str__", "gameweek", "date", "status"]
    search_fields = ["awayTeam__name", "homeTeam__name", "gameweek"]


@admin.register(SeasonInfo)
class SeasonInfoAdmin(admin.ModelAdmin):
    readonly_fields = ["gameweek"]


admin.site.register(Player)
admin.site.register(User)
admin.site.register(Clients)