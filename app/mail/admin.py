from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from mail.models import SmtpServer, AsyncMail


@admin.register(SmtpServer)
class SmtpServerAdmin(admin.ModelAdmin):
    pass


@admin.register(AsyncMail)
class AsyncMailAdmin(admin.ModelAdmin):
    pass
