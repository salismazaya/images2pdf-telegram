from django.urls import re_path
from django.conf import settings
from main import views
import re

urlpatterns = [
    re_path('^supersecret/hooks/{}/?$'.format(settings.TELEGRAM_BOT_TOKEN), views.webhook, name = 'webhook')
]