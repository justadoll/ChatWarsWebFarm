from django.urls import path, include
from main.views import index, indiv_player, send_command, update_qr_and_auth, give_qr_img, ChwCreateView, login_required


urlpatterns = [
        path("", index, name="main"),
        path('add/', login_required(ChwCreateView.as_view()), name="add"),
        path('add/upd/', update_qr_and_auth, name="auth_player"),
        path('add/get_qr/', give_qr_img, name="get_qr"),
        path('players/', include(("main.players_urls","players_urls"), namespace="players_urls")),
        path('player/<int:pk>/',indiv_player, name="player"),
        path('player/<int:pk>/command/',send_command, name="command"),
        ]
