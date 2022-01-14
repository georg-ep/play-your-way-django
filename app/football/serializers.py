from rest_framework import serializers
from .models import Match, Team, Player


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class MatchListSerializer(serializers.ModelSerializer):
    awayTeam = TeamSerializer()
    homeTeam = TeamSerializer()

    class Meta:
        model = Match
        fields = "__all__"


class PlayerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"


class ListTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class HomeMatchSerializer(serializers.ModelSerializer):
    awayTeam = TeamSerializer()

    class Meta:
        model = Match
        fields = ["match_id", "date", "awayTeam"]


class AwayMatchSerializer(serializers.ModelSerializer):
    homeTeam = TeamSerializer()

    class Meta:
        model = Match
        fields = ["match_id", "date", "homeTeam"]


class DetailTeamSerializer(serializers.ModelSerializer):
    players = PlayerDetailSerializer(
        many=True,
        read_only=True,
    )
    home_games = HomeMatchSerializer(
        many=True,
        read_only=True,
    )
    away_games = AwayMatchSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Team
        fields = "__all__"
