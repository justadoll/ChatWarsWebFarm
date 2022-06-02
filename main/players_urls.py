from django.urls import path
from .views import players_list
from .players_controller import commander, atck_def, status_all

urlpatterns = [
        path('', players_list, name="all_players_in_db"),
        path("status/", status_all, name="status"),
        path("command/", commander, name="command"),
        path("atck_def/", atck_def, name="atck_def"),
        ]