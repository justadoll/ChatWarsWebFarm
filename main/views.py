from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .serializers import PlayerSerializer
from loguru import logger

from .chw_manager import ChwMaster
import asyncio
from channels.db import database_sync_to_async

chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)

def chw_manager(action, id):
    # TODO: mathces for `action` from python3.10?
    # https://stackoverflow.com/questions/62390314/how-to-call-asynchronous-function-in-django
    player = CW_players.objects.get(pk=id)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if action == "get_user_data":#TODO POST create and insert info to new chatWarsPlayers table
        async_result = loop.run_until_complete(chw_master.get_user_data(player))
        logger.debug(async_result)
        loop.close()
    elif action == "quest_run":
        async_result = loop.run_until_complete(chw_master.mainQuestRun(player,6))
        logger.debug(async_result)
        loop.close()
    elif action == "get_game_time":
        async_result = loop.run_until_complete(chw_master.get_game_time(player))
        loop.close()
        return async_result
    else:
        logger.error("wtf?")

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
            for test in serializer:
                if test.value == "Run":
                    #logger.debug("Run, forest, run!")
                    #chw_manager("quest_run", player.pk)
                    #logger.info(chw_manager("get_game_time", player.pk))
                    logger.info(chw_manager("get_user_data", player.pk))

                    return JsonResponse(serializer.data)
                else:
                    pass
            return JsonResponse({"response":"Something gone wrong"}, status=401)
        return JsonResponse(serializer.errors, status=400)


def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})
