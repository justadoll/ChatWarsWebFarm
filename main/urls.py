from django.urls import path
from django.conf.urls import url
from main.views import index, players_list, indiv_player, send_command, send_phone_request, ChwCreateView


urlpatterns = [
        path("", index, name="main"),
        path('add/', ChwCreateView.as_view(), name="add"),
        path('add/send_code', send_phone_request, name="send_code"),
        path('players/',players_list, name="players"),
        path('player/<int:pk>/',indiv_player, name="player"),
        path('player/<int:pk>/command/',send_command, name="command"),
        ]
