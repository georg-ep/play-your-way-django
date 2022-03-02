from django.shortcuts import render
from football.models import Player
from rest_framework import generics
from .serializers import CreateBetSerializer, ListBetSerializer, BetScorerSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Bet, BetScorer
from django.db.models import Q

# Create your views here.

# TODO make this a creare oject


@api_view(["POST"])
def accept_bet(request, bet_id):
    user = request.user
    bet = Bet.objects.filter(id=bet_id).first()
    if not bet.user2 == user and bet.is_accepted == False:
        return Response({"detail": "Error finding bet"})
    bet.is_accepted = True
    bet.save()
    return Response({"status": "OK"})


class DetailBetView(generics.RetrieveAPIView):
    queryset = Bet.objects.all()
    serializer_class = ListBetSerializer

class CreateBetScorerView(generics.CreateAPIView):
    serializer_class = BetScorerSerializer


class CreateBetView(generics.CreateAPIView):
    serializer_class = CreateBetSerializer


class MyBets(generics.ListAPIView):
    queryset = Bet.objects.all()
    serializer_class = ListBetSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Bet.objects.filter(Q(user1=user) | Q(user2=user))
        queryset = queryset.filter(is_accepted=True)
        return queryset


class ListPendingBetsView(generics.ListAPIView):
    serializer_class = ListBetSerializer

    def get_queryset(self):
        user = self.request.user
        return Bet.objects.filter(user1=user).filter(is_accepted=False)

class ListReceivedBetsView(generics.ListAPIView):
    serializer_class = ListBetSerializer

    def get_queryset(self):
        user = self.request.user
        return Bet.objects.filter(user2=user).filter(is_accepted=False)

# class ListConfirmedBetsView(generics.ListAPIView):
#   serializer_class = ListBetSerializer

#   def get_queryset(self):
#     user = self.request.user
#     return Bet.objects.filter(user1=)
