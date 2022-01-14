from django.urls import path, re_path, include
from football import views

urlpatterns = [
    path("fixtures/<int:gameweek>/", views.ListMatchView.as_view(), name="fixtures"),
    path("fixture/<int:pk>/", views.DetailMatchView.as_view(), name="detail"),
    path("team/list/", views.ListTeamView.as_view(), name="team-list"),
    path("team/detail/<int:pk>/", views.DetailTeamView.as_view(), name="team-detail"),
    path("loadData/", views.load_data, name="load-data"),
    path("test/", views.test,),
    path("fetch-current-gameweek/", views.current_gameweek),
]
