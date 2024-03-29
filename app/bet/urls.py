from django.urls import path, re_path, include
from bet import views

urlpatterns = [
    path("create/", views.CreateBetView.as_view(), name="create"),
    path("pending/", views.ListPendingBetsView.as_view(), name="pending"),
    path("received/", views.ListReceivedBetsView.as_view(), name="received"),
    path("detail/<int:pk>/", views.DetailBetView.as_view(), name="detail"),
    path("accept/<int:bet_id>/", views.accept_bet, name="accept-bet"),
    path("mine/", views.MyBets.as_view(), name="my-bets"),
    path(
        "add-player/",
        views.CreateBetScorerView.as_view(),
        name="create-bet-scorer",
    ),
]
