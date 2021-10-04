from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CW_players
from .serializers import PlayerSerializer

def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = CW_players.objects.all().order_by('-registration_date')
    serializer_class = PlayerSerializer
