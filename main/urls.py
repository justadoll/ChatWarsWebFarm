from django.urls import path, include
from rest_framework import routers
#from .views import index
from . import views


router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewSet)

urlpatterns = [
        path('',include(router.urls)),
        #path('',index, name='main'),
        ]
