from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from football import models as football_models
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = "Checks all fixtures to create a task to fetch live data"

    def handle(self, *args, **options):

        # test times 
        lb = datetime.now(tz=timezone.utc) - timedelta(minutes=30)
        ub = datetime.now(tz=timezone.utc) + timedelta(minutes=30)

        fixtures = football_models.Match.objects.filter(date__gt=lb).filter(date__lt=ub)

        for match in fixtures:
            if not PeriodicTask.objects.filter(name=f"match-{match.match_id}").exists():
                print(f"Scheduling task for {match} at {match.date}")
                schedule = IntervalSchedule.objects.create(
                    every=1, period=IntervalSchedule.MINUTES
                )

                task = PeriodicTask.objects.create(
                    interval=schedule,
                    start_time=match.date,
                    name=f"match-{match.match_id}",
                    task="fetch-live-game",
                    args=json.dumps([match.match_id]),
                )
                task.save()