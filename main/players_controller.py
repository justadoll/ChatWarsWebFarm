from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.conf import settings
from .models import CW_players
from .serializers import PlayerSerializer
from .chw_manager import ChwMaster
from .views import chw_master
import asyncio

logger = settings.LOGGER

def chw_all_players_mng(action:str, players:list, target:str=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if action == "atck" and target:
        async_result = loop.run_until_complete(chw_master.atack(players_list=players, target=target))
    elif action == "def":
        async_result = loop.run_until_complete(chw_master.defc(players_list=players))
    elif action == "status":
        async_result = loop.run_until_complete(chw_master.status(players_list=players))
    elif action == "command":
        async_result = loop.run_until_complete(chw_master.command(players_list=players, command=target))
    logger.info(f"{async_result=}")
    loop.close()
    loop.stop()
    return async_result

@api_view(["GET"])
def status_all(request):
    players_list = []
    players = CW_players.objects.all()
    for player in players:
        players_list.append(player)
    try:
        response = chw_all_players_mng(action="status", players=players_list)
    except Exception as e:
        return JsonResponse({"status":"error"}, status=400)
    else:
        return JsonResponse({"status":response}, status=200)

@api_view(["POST"])
def commander(request):
    players_list = []
    players = CW_players.objects.all()
    for player in players:
        players_list.append(player)
    data = JSONParser().parse(request)
    logger.debug(f"{data['command']=}")
    response = chw_all_players_mng(action="command", players=players_list, target=data['command'])

    return JsonResponse({"status":response}, status=200)
    
@api_view(["POST"])
def atck_def(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        players_list = []
        players = CW_players.objects.all()
        for player in players:
            players_list.append(player)
        if data['action'] == "atck":
            logger.debug(f"Atack on {data['castle']}!")
            response = chw_all_players_mng(action="atck", players=players_list, target=data['castle'])
        elif data['action'] == "def":
            logger.debug("Defence!")
            response = chw_all_players_mng(action="def", players=players_list)
        else:
            logger.warning(f"Unknown command: {data=}")
            return JsonResponse({"status":"Unknown command"}, status=400)
        return JsonResponse({"status":response}, status=200)