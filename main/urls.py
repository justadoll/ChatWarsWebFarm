from django.urls import path, include
from main.views import index, players_list, indiv_player, send_phone_request, ChwCreateView


#router = routers.DefaultRouter()
#router.register(r'players', views.PlayerViewSet)

urlpatterns = [
        path('', index, name='main'),
        path('add/', ChwCreateView.as_view(), name="add"),
        path('add/send_code', send_phone_request, name="send_code"),
        path('players/',players_list),
        path('player/<int:pk>/',indiv_player),
        ]
