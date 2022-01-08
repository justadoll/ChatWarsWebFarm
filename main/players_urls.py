from django.urls import path
from .players_controller import commander, atck_def, status_all

urlpatterns = [
        path("status/", status_all, name="status"),
        path("command/", commander, name="command"),
        path("atck_def/", atck_def, name="atck_def"),
        ]