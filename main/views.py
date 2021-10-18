from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .serializers import PlayerSerializer
from loguru import logger


@api_view(['GET','POST'])
def players_list(request):
    if request.method == 'GET':
        players = CW_players.objects.all()
        serializer = PlayerSerializer(players, fields=('id','chw_username','status','player_class'), many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET','PUT'])
def indiv_player(request,pk):
    try:
        player = CW_players.objects.get(pk=pk)
    except CW_players.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PlayerSerializer(player,fields=('id','chw_username','username','status','player_class'))
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = PlayerSerializer(player, data=data, fields=('id','chw_username','username','status'))
        if serializer.is_valid():
            serializer.save()
            logger.debug(player.session)
            # threads or recode to async?
            for test in serializer:
                if test.value == "Run":
                    logger.debug("Run, forest, run!")
                    return JsonResponse(serializer.data)
                else:
                    pass
            return JsonResponse({"response":"Something gone wrong"}, status=401)
        return JsonResponse(serializer.errors, status=400)


def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})
