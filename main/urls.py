from django.urls import path, include
from main import views


#router = routers.DefaultRouter()
#router.register(r'players', views.PlayerViewSet)

urlpatterns = [
        path('', views.index, name='main'),
        path('players/',views.players_list),
        path('player/<int:pk>/',views.indiv_player),
        ]
