from django.urls import path
from probot.main import views as main_views

urlpatterns = [
  path('probot/', main_views.telegram_bot, name='telegram_bot'),
  path('setwebhook/', main_views.setwebhook, name='setwebhook'), 
]
