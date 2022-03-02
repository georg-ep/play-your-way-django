from rest_framework import serializers
from .models import Bet, BetScorer
from user.serializers import UserDetailSerializer
from football.serializers import MatchListSerializer, PlayerDetailSerializer
import json
from football.serializers import TeamSerializer


class CreateBetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = "__all__"


class BetScorerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetScorer
        fields = ["bet", "player"]


class BetScorerDetailSerializer(serializers.ModelSerializer):
    player = PlayerDetailSerializer()

    class Meta:
        model = BetScorer
        fields = ["player"]


class ListBetSerializer(serializers.ModelSerializer):
    match = MatchListSerializer()
    opponent = serializers.SerializerMethodField()
    scorers = BetScorerDetailSerializer(many=True, read_only=True)
    winner = TeamSerializer()

    def get_opponent(self, obj):
        user = self.context["request"].user
        if user == obj.user1:
            opponent = UserDetailSerializer(obj.user2).data
            return opponent
        else:
            opponent = UserDetailSerializer(obj.user1).data
            return opponent

    class Meta:
        model = Bet
        fields = ["id", "opponent", "match", "amount", "winner", "scorers"]
