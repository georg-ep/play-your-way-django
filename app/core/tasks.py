from datetime import datetime
from celery import shared_task
from celery.signals import worker_init, worker_shutdown

from core.redis import redis_storage
import requests
from storages.utils import setting
import json
from football.models import SeasonInfo, Match
from .celery import app as celery_app


@worker_init.connect
def on_worker_init(*_, **__):
    keys = redis_storage.connection.keys("running_tasks:*")

    if keys:
        redis_storage.connection.delete(*keys)


@worker_shutdown.connect
def on_worker_shutdown(*_, **__):
    redis_storage.connection.close()


"""
FLOW

"""

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



@shared_task(name="fetch-live-game")
def fetch_live_game(match_id):
    match = Match.objects.filter(match_id=match_id).first()
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    url = API_URL + f"matches/{match_id}"
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)["match"]
    winner = None
    match.status = data["status"]
    if data["score"]["winner"] == "HOME_TEAM":
          winner = data["homeTeam"]["id"]
    if data["score"]["winner"] == "AWAY_TEAM":
          winner = data["awayTeam"]["id"]
    match.save()

# Update data for games which have been postponed and rescheduled, 1 time a day
@shared_task(name="fetch-games-data")
def fetch_games_data():
    API_URL = setting("FOOTBALL_URL")
    headers = {"X-Auth-Token": "deb08a34530649d3a2d946b13b18712d"}
    response = requests.get(API_URL + "competitions/PL/matches/", headers=headers)
    matches = json.loads(response.content)["matches"]

    for match in matches:
        d_match = Match.objects.filter(match_id=match["id"]).first()

        if d_match != None:

            winner = None
            if match["score"]["winner"] == "HOME_TEAM":
                winner = match["homeTeam"]["name"]
            elif match["score"]["winner"] == "AWAY_TEAM":
                winner = match["awayTeam"]["name"]
            elif match["socre"]["winner"] == "DRAW":
                winner = "Draw"
            else:
                winner = None
            match.winner = winner


            score = None
            if winner == None:
                score = False
              


            if d_match.status != match["status"]:
                print("status changed for", match)
                d_match.status = match["status"]
                d_match.save()


            match_date = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            date_changed = d_match.date != match_date
            if date_changed:
                print("date changed")
                print("api", match_date)
                print("dtb", d_match.date)
                d_match.date = match_date
            d_match.save()