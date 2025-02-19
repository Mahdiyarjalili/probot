
from django.contrib import admin
from django.urls import path, include

TELEGRAM_BOT_HANDLERS_CONF = "app.handlers"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('probot.main.urls')), # new
 
]
