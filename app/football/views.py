from django.shortcuts import render
from rest_framework import generics
import requests
from storages.utils import setting
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .models import Match, SeasonInfo, Team, Player
from datetime import date, datetime, timedelta, tzinfo
from football import serializers
import django_filters.rest_framework
from rest_framework import filters

# Create your views here.


class ListTeamView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = serializers.ListTeamSerializer


class DetailTeamView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = serializers.DetailTeamSerializer


# class ListMatchView(generics.ListAPIView):
#     queryset = Match.objects.all()
#     serializer_class = serializers.MatchListSerializer
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
#     filterset_fields = ["gameweek"]

class ListUpcomingMatchesView(generics.ListAPIView):
    queryset = Match.objects.all()
    serializer_class = serializers.MatchListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        current = datetime.now()
        return queryset.filter(date__gt=current)

class ListMatchView(generics.ListAPIView):
    queryset = Match.objects.all()
    serializer_class = serializers.MatchListSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_fields = ["status"]
    search_fields = ["homeTeam__name", "awayTeam__name"]
    ordering = ["-date"]


class GameweekMatchView(generics.ListAPIView):
    serializer_class = serializers.MatchListSerializer
    queryset = Match.objects.all()

    def get_queryset(self):
        gameweek = self.kwargs["gameweek"]
        return super().get_queryset().filter(gameweek=gameweek)


@api_view(["GET"])
def current_gameweek(request):
    seasonInfo = SeasonInfo.objects.first()
    return Response({"gameweek": seasonInfo.gameweek})


class DetailMatchView(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = serializers.MatchListSerializer


def create_team(team_id):
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(API_URL + f"/teams/{team_id}/", headers=headers)
    team_data = json.loads(response.content)
    print(team_data)
    team = Team()
    team.team_id = team_id
    try:
        team.name = team_data["shortName"]
    except Exception as e:
        print(e)
    team.venue = team_data["venue"]
    team.save()
    print(f"created team, {team}")
    create_players_for_team(team_data["squad"], team)


from django_celery_beat.models import PeriodicTask, IntervalSchedule, ClockedSchedule
from django.utils import timezone


@api_view(["GET"])
def test(request):
    # lb = datetime.now(tz=timezone.utc) - timedelta(minutes=30)
    # ub = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(API_URL + f"competitions/PL/teams/", headers=headers)
    teams = json.loads(response.content)
    l_teams = Team.objects.all()
    for team in teams["teams"]:
        l_team = l_teams.filter(team_id=team["id"]).first()
        l_team.crest = team["crestUrl"]
        l_team.save()
        print("saving crest")

    # lb = datetime.now(tz=timezone.utc)
    # ub = datetime.now(tz=timezone.utc) + timedelta(days=1)
    # print("lb", lb)
    # print("ub", ub)
    # seasonInfo = SeasonInfo.objects.first()
    # gameweek = seasonInfo.gameweek + 1
    # matches = Match.objects.filter(date__lt=ub).filter(date__gt=lb)
    # for match in matches:
    #     if not PeriodicTask.objects.filter(name=f"match-{match.match_id}").exists():
    #         print(f"Scheduling task for {match} at {match.date}")
    #         schedule = IntervalSchedule.objects.create(
    #             every=10, period=IntervalSchedule.SECONDS
    #         )
    #         task = PeriodicTask.objects.create(
    #             interval=schedule,
    #             start_time=match.date,
    #             name=f"match-{match.match_id}",
    #             task="fetch-live-game",
    #             args=json.dumps([match.match_id]),
    #         )
    #         task.save()
    # task = PeriodicTask.objects.filter(name="live-game-data").first()
    # if task:
    #     if task.enabled == True:
    #         task.enabled = False
    #     else:
    #         task.enabled = True
    #     task.save()
    # else:
    #     schedule = IntervalSchedule.objects.create(
    #         every=10, period=IntervalSchedule.SECONDS
    #     )
    #     task = PeriodicTask.objects.create(
    #         interval=schedule, name="live-game-data", task="fetch-games-data"
    #     )
    #     task.save()

    return Response({"detail": "OK"})


@api_view(["GET"])
def load_data(request):
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(
        API_URL + "competitions/PL/matches?status=SCHEDULED", headers=headers
    )
    data = json.loads(response.content)
    matches = data["matches"]

    for match in matches:
        homeTeamId = match["homeTeam"]["id"]
        awayTeamId = match["awayTeam"]["id"]
        if not Match.objects.filter(pk=match["id"]).exists():
            if not Team.objects.filter(team_id=homeTeamId).first():
                create_team(homeTeamId)
            if not Team.objects.filter(team_id=awayTeamId).first():
                create_team(team_id=awayTeamId)
            date = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            homeTeam = Team.objects.filter(team_id=homeTeamId).first()
            awayTeam = Team.objects.filter(team_id=awayTeamId).first()
            m = Match.objects.create(
                match_id=match["id"],
                homeTeam=homeTeam,
                awayTeam=awayTeam,
                gameweek=match["matchday"],
                date=date,
            )
            m.save()
    return Response(matches)


def create_players_for_team(squad, team):

    for player in squad:
        p = Player(
            team=team,
            player_id=player["id"],
            name=player["name"],
            position=player["position"],
            nationality=player["nationality"],
            shirtNumber=player["shirtNumber"],
        )
        p.save()
        print(f"added {p} to {team}")
