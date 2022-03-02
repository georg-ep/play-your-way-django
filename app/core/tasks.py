from datetime import datetime
from celery import shared_task
from celery.signals import worker_init, worker_shutdown

from core.redis import redis_storage
import requests
from storages.utils import setting
import json
from football.models import SeasonInfo, Match, Team
from django_celery_beat.models import PeriodicTask
from django.utils import timezone
from celery.signals import worker_ready
from bet import models as bet_models


@worker_init.connect
def on_worker_init(*_, **__):
    keys = redis_storage.connection.keys("running_tasks:*")
    if keys:
        redis_storage.connection.delete(*keys)


@worker_shutdown.connect
def on_worker_shutdown(*_, **__):
    redis_storage.connection.close()


# When server has been down for a while, ensure data is up to date
@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
        sender.app.send_task("fetch-current-gameweek")
        sender.app.send_task("fetch-games-data")


#  Fetches current gameweek
@shared_task(name="fetch-current-gameweek")
def fetch_current_gameweek():
    """
    Fetches current gameweek used for fetching fixtures
    """
    print("Fetching current gameweek...")
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(API_URL + "competitions/PL/", headers=headers)
    matchWeek = json.loads(response.content)["currentSeason"]["currentMatchday"]
    seasonInfo = SeasonInfo.objects.first()
    if seasonInfo:
        if seasonInfo.gameweek != matchWeek:
            seasonInfo.gameweek = matchWeek
            seasonInfo.save()
            print("Gameweek has changed, updated...")
    else:
        print("No instance of season info found, creating instance")
        seasonInfo = SeasonInfo(gameweek=matchWeek)
        seasonInfo.save()
        print("Season info created, gameweek is updated")
    print("Success, current gameweek is", seasonInfo.gameweek)


@shared_task(name="fetch-live-game")
def fetch_live_game(match_id):
    match = Match.objects.filter(match_id=match_id).first()
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    url = API_URL + f"matches/{match_id}"
    response = requests.get(url, headers=headers)
    print(f"Beating for {match.homeTeam.name} - {match.awayTeam.name}")
    data = json.loads(response.content)["match"]
    finish_task = False

    if data["status"] != match.status:
        match.status = data["status"]
        if data["status"] == "FINISHED":
            finish_task = True

    score = data["score"]

    if score["winner"] != match.winner:
        if score["winner"] == "HOME_TEAM":
            match.winner = match.homeTeam.name
        if score["winner"] == "AWAY_TEAM":
            match.winner = match.awayTeam.name
        if score["winner"] == "DRAW":
            match.winner == "Draw"

    live_states = ["LIVE", "IN_PLAY", "PAUSED", "FINISHED"]

    if data["status"] in live_states:
        halfTime = score["halfTime"]
        fullTime = score["fullTime"]

        if not fullTime["homeTeam"] == None and not fullTime["awayTeam"] == None:
            match.home_goals = fullTime["homeTeam"]
            match.away_goals = fullTime["awayTeam"]
        else:
            match.home_goals = halfTime["homeTeam"]
            match.away_goals = halfTime["awayTeam"]

    match.save()

    if finish_task:
        task = PeriodicTask.objects.filter(name=f"match-{match_id}")
        print(f"match {match_id} finished, cancelling it")
        task.delete()
        bets = bet_models.Bet.objects.filter(match=match)
        if not bets:
            print("No bets placed on this game")
            return
        for bet in bets:
            # user1 wins on placed bet
            if bet.winner.name == match.winner:
                bet.bet_winner = bet.user1
            if bet.winner.name != match.winner and match.winner != None:
                bet.bet_winner = bet.user2
            if bet.winner == None and match.winner == "Draw":
                bet.bet_winner = bet.user1
            if bet.winner == None and match.winner != "Draw":
                bet.bet_winner = bet.user2

            winner = bet.bet_winner
            print("winner is", winner.email)
            if winner is not None:
              winner.credits += bet.amount
              winner.save()

            bet.is_settled = True
            bet.save()


# Update data for games which have been postponed and rescheduled, 1 time a day
@shared_task(name="fetch-games-data")
def fetch_games_data():
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(API_URL + "competitions/PL/matches/", headers=headers)
    matches = json.loads(response.content)["matches"]

    new_data = False

    for match in matches:
        d_match = Match.objects.filter(match_id=match["id"]).first()

        if d_match == None:
            # create new match if one doesn't exist.
            print("Creating new match")
            new_data = True
            homeTeam = Team.objects.filter(team_id=match["homeTeam"]["id"]).first()
            awayTeam = Team.objects.filter(team_id=match["awayTeam"]["id"]).first()
            d_match = Match(
                match_id=match["id"],
                awayTeam=awayTeam,
                homeTeam=homeTeam,
                gameweek=match["matchday"],
            )

        winner = None
        if match["score"]["winner"] == "HOME_TEAM":
            winner = match["homeTeam"]["name"]
        elif match["score"]["winner"] == "AWAY_TEAM":
            winner = match["awayTeam"]["name"]
        elif match["score"]["winner"] == "DRAW":
            winner = "Draw"
        else:
            winner = None
        d_match.winner = winner

        score = match["score"]["fullTime"]

        if (
            score["homeTeam"] != d_match.home_goals
            or score["awayTeam"] != d_match.away_goals
        ):
            new_data = True
            print("score changed for", d_match)
            d_match.away_goals = score["awayTeam"]
            d_match.home_goals = score["homeTeam"]

        if d_match.status != match["status"]:
            new_data = True
            print("status changed for", d_match)
            d_match.status = match["status"]

        match_date = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        date_changed = d_match.date.replace(tzinfo=timezone.utc) != match_date
        if date_changed:
            new_data = True
            print("date changed for", d_match)
            d_match.date = match_date

        d_match.save()

    if not new_data:
        print("No new data found")
