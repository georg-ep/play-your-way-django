import time

from django.core.management import BaseCommand

from mail.models import AsyncMail


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = AsyncMail.objects.filter(status=AsyncMail.STATUS_NEW, batch=True).all()[:50]
        print(f'Emails in batch: {len(models)}')
        for model in models:
            print(f"Sending email from batch: {model.id}...")
            model.send()
            model.batch = False
            print(model.error_message)
            time.sleep(1)
