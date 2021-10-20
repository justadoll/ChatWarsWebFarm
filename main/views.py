from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .serializers import PlayerSerializer
from loguru import logger

from .chw_manager import *
import asyncio
from channels.db import database_sync_to_async


"""
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
"""

def chw_manager(action, id):
    # TODO: mathces for `action` from python3.10?
    # https://stackoverflow.com/questions/62390314/how-to-call-asynchronous-function-in-django
    player = CW_players.objects.get(pk=id)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if action == "get_user_data":#TODO POST create and insert info to new chatWarsPlayers table
        async_result = loop.run_until_complete(get_user_data("1ApWapzMBu3P1gqGRIb-6nhKhjSGJSHktSVqa9E37cftifP4zCwv2u0pANr8iPQw13ueNzUWRrJn3fbAlwFiN6y4X9zkB1l2BnC5_XLjrg91IsJNBxyFqeyJy6O9oXVJ2f-nhYuqt0Wx-RPbuXP2TKyMsfqrmiBdWIcxLwqQnkFA8hEDcX2dyEwQUylbR83B_Ka3N99-ku-RkIFEs5EQ0-6rkTHXD7FA8Hn_DpDBcC0HYueYw9zdKphqtfKkZ1_38d3Y0SzbXlotoiunXjP3P6mE2c6h-nfIs3W7HuEUHZxrrmaqxwDYf5Db0R1ylAXy--HTYeAa9jFSyGF6t1wvD1dHyF8LReNA="))
        logger.debug(async_result)
        loop.close()
    elif action == "quest_run":
        async_result = loop.run_until_complete(mainQuestRun(player,3))
        #async_result = loop.run_until_complete(mainQuestRun("1ApWapzMBu03MvpeDgB0qC81VWCu4r7dxrUaAx8lE5FYP_fwnuk_ifFCdh0L5Psee_Sm-g__ZH9SDoOxcWxjgoFmcSRL9lLGmq1QDKSMf6pEN0CpI4qFfgM0OrnKigM4hAfXb_GFesTLVT3o2cDoKEQshrBf3oXzRrzX1MRKG4dA5I7gv1UQIFtHaABUuZcW8kIgKUgtSN4QMBoaiU4SMh0iqCGnqGqLD3c7Ex6OqJhG77JVbH4UPbwdFIdkUP93PD9sHfAp94se-HoeDtslELxUqL8cYFb7ARj04s2K4cJAL3K1vtBJKofHIggRfrAKVjvo4qfqb1y4Y3-aHnZArQrlvcAx_g5o=",3))
        logger.debug(async_result)
        loop.close()
    elif action == "get_game_time":
        async_result = loop.run_until_complete(get_game_time(player))
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
                    logger.debug("Run, forest, run!")
                    chw_manager("quest_run", player.pk)
                    #logger.info(chw_manager("get_game_time", player.pk))
                    return JsonResponse(serializer.data)
                else:
                    pass
            return JsonResponse({"response":"Something gone wrong"}, status=401)
        return JsonResponse(serializer.errors, status=400)


def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})
