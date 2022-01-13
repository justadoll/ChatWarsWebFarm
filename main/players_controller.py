from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import CW_players
from .views import chw_master, csrf_exempt
import asyncio

logger = settings.LOGGER
json_messages = settings.JSON_MESSAGES

def fast_sec_check(request):
    if request.method == "POST":
        players = CW_players.objects.filter(user=request.user)
        if not players:
            logger.warning(f"User {request.user} trying to send COMMAND/ATCK-DEF for ALL players but hasn't any player!")
            return JsonResponse(json_messages['no_players'], status=403)
        else:
            return players
    logger.warning(f"User {request.user} trying to send COMMAND/ATCK-DEF for ALL players not buy correct method!")
    return JsonResponse(json_messages['forb_meth'], status=403)
        


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
    logger.debug(f"{async_result=} for {players=} and {target=}")
    loop.close()
    loop.stop()
    return async_result

@api_view(["GET"])
@login_required
def status_all(request):
    players = CW_players.objects.filter(user=request.user)
    if not players:
        logger.warning(f"User {request.user.username} trying to get ALL info about players but haven't any")
        return JsonResponse(json_messages['no_players'], status=403)
    try:
        response = chw_all_players_mng(action="status", players=players)
    except Exception as e:
        return JsonResponse({"status":"error"}, status=400)
    else:
        logger.success(f"User {request.user.username} got ALL info about players")
        return JsonResponse({"status":response}, status=200)

#@api_view(["POST"])
@login_required
@csrf_exempt
def commander(request):
    response_checker = fast_sec_check(request)
    if type(response_checker) is not JsonResponse:
        data = JSONParser().parse(request)
        logger.info(f"{request.user.username} send command {data['command']} for all his players")
        response = chw_all_players_mng(action="command", players=response_checker, target=data['command'])

        return JsonResponse({"status":response}, status=200)
    else:
        return response_checker
    
#@api_view(["POST"])
@login_required
@csrf_exempt
def atck_def(request):
    response_checker = fast_sec_check(request)
    if type(response_checker) is not JsonResponse:
        data = JSONParser().parse(request)
        if data['action'] == "atck":
            logger.info(f"{request.user.username} [ATCK] {data['castle']} by all his players")
            response = chw_all_players_mng(action="atck", players=response_checker, target=data['castle'])
        elif data['action'] == "def":
            logger.info(f"{request.user.username} makes [DEF] for all his players")
            response = chw_all_players_mng(action="def", players=response_checker)
        else:
            logger.warning(f"Unknown command: {data=} from {request.user.username} user")
            return JsonResponse({"status":"Unknown command"}, status=400)
        return JsonResponse({"status":response}, status=200)
    else:
        return response_checker