from pyexpat import model
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .tasks import make_qr_login, run_quest_task, def_cow_task
from .serializers import PlayerSerializer
from .forms import ChwForm

from .chw_manager import ChwMaster
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
import asyncio

logger = settings.LOGGER
redis = settings.REDIS
chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)
json_messages = settings.JSON_MESSAGES


def auth_new_player():
    response = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client, task = loop.run_until_complete(make_qr_login())
    logger.info(f"{settings.QR_LOGIN_TEXT=}")
    logger.debug("Handling task on login")
    try:
        loop.run_until_complete(task)
    except SessionPasswordNeededError:
        response["status"] = "2FA"
        response["status_code"] = 401
    except asyncio.exceptions.TimeoutError:
        logger.error("Timeout!")
        response["status"] = "timeout"
        response["status_code"] = 408
    else:
        session = client.session.save()
        response["status"] = "success"
        response["status_code"] = 200
        response["session"] = session
    loop.close()
    return response

def chw_manager(action, id, button=None, command=None):
    # https://stackoverflow.com/questions/62390314/how-to-call-asynchronous-function-in-django
    player = CW_players.objects.get(pk=id)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if action == "get_user_data":
        async_result = loop.run_until_complete(chw_master.get_user_data(player))
        logger.debug(async_result)
    elif action == "quest_run":
        async_result = loop.run_until_complete(chw_master.mainQuestRun(player, button))
        logger.debug(async_result)
        player.status="🛌Sleep"
        player.save()
    elif action == "get_info":
        async_result = loop.run_until_complete(chw_master.get_player_info(player))
        return async_result
    elif action == "get_game_time":
        async_result = loop.run_until_complete(chw_master.get_game_time(player))
        return async_result
    elif action == "chat_shell":
        async_result = loop.run_until_complete(chw_master.chat_shell(player,command))
        return async_result
    else:
        logger.error("wtf?")
    loop.close()

@api_view(['GET'])
@login_required
def players_list(request):
    players = CW_players.objects.filter(user=request.user)
    logger.info(f"{request.user.username} getting info from DB about ALL players")
    serializer = PlayerSerializer(players, fields=('id','chw_username','status','player_class'), many=True)
    return JsonResponse(serializer.data, safe=False)

#@api_view(['GET','PUT','POST', 'DELETE'])
@login_required
@csrf_exempt
def indiv_player(request,pk):
    try:
        player = CW_players.objects.filter(user=request.user, pk=pk)
        if not player:
            logger.warning(f"User {request.user} trying to get info about not his bot by {pk=}")
            return JsonResponse(json_messages['forbidden'], status=403)
        else:
            player = player[0]
            logger.info(f"User {request.user} getting info about {player.chw_username}:{player.pk}")
    except CW_players.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PlayerSerializer(player,fields=('id','chw_username','username','status','player_class'))
        new_data = chw_manager("get_info", player.pk)
        if not new_data:
            context = {"status": "Player logouted!"}
            logger.error(f"{request.user.username} got logouted player {player.chw_username}:{player.pk=}")
            return render(request, 'main/error.html', context)
        player.chw_username = new_data['player_username']
        player.player_class = new_data['player_class']
        player.lvl = new_data['lvl']
        player.username = new_data['username']
        player.phone_number = new_data['phone']
        if player.status == "":
            player.status = "🛌Sleep"
        player.save()
        context = {'id':serializer.data['id'], 'username':serializer.data['chw_username'], 'status':new_data['status'], 'class':serializer.data['player_class'],'lvl':new_data['lvl'],'lvlup':new_data['lvlup']}
        logger.info(f"{request.user.username} updates info about {player.chw_username}:{player.pk=}")
        return render(request, 'main/player.html', context)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        button2int = {"forest": 0, "swamp": 1, "mount": 2, "cow": 3}
        str_button = data['quest']
        logger.info(f"{request.user.username} sent player {player.chw_username}:{player.pk=} to {button2int[str_button]=}")
        if(player.status=="Run"):
            logger.warning(f"User {request.user.username} with player {player.chw_username}:{player.pk=} already run!")
            return JsonResponse({"response":"Player already run!"}, status=208)
        else:
            after_status = player.status
            serializer = PlayerSerializer(player, data=data, fields=('id','status'))
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {request.user.username} with player {player.chw_username}:{player.pk=} started runnig quest!")
                task = run_quest_task.delay(p_id=player.pk, button=button2int[str_button], after_status=after_status)
                logger.debug(f"{task.id=}")
                return JsonResponse({"response":"Runnig quest!"}, status=200)
            else:
                logger.error(f"{request.user.username=} {player.chw_username}:{player.pk=} {serializer.errors=}")
                return JsonResponse({"response":"Something gone wrong"}, status=401)

    elif request.method == "DELETE":
        try:
            player.delete()
        except Exception as e:
            logger.error(f"{request.user.username=} {player.chw_username}:{player.pk=} {e=}")
            return JsonResponse({"status":"Something gone wrong!"}, status=400)
        else:
            logger.success(f"User {request.user.username} deleted {player.chw_username}:{player.pk=}")
            return JsonResponse({"status":"OK"}, status=200)

    elif request.method == "POST":
        player = CW_players.objects.get(pk=pk)
        task = def_cow_task.delay(user=request.user.username, pk=pk)
        player.defcow = task.id
        player.save()
        logger.debug(f"{player.chw_username} def-cow id: {task.id}")
        return JsonResponse({"status":"OK"}, status=200)
        # TODO user revoke def-cow
        # >>> from ChatWarsWebFarm.celery import celery_app
        # >>> celery_app.control.revoke("10273f33-1cce-4bd2-a3a7-78d4b01ec407")

#@api_view(['PUT'])
@login_required
@csrf_exempt
def send_command(request, pk:int):
    if request.method == "PUT":
        data = JSONParser().parse(request)
        logger.info(f"{request.user.username} send command: {data}")
        player = CW_players.objects.filter(user=request.user, pk=pk)
        if not player:
            logger.warning(f"User {request.user.username} trying to get info about not his player by {pk=}")
            return JsonResponse(json_messages['forbidden'], status=403)
        response = chw_manager(action="chat_shell", id=player[0].pk, command=data['command'])
        logger.success(f"User {request.user.username} got {response=}")
        
        return JsonResponse({"result":response}, status=200)
    else:
        return JsonResponse(json_messages['forb_meth'], status=403)

@login_required
def index(request):
    logger.debug(f"{request.user.username} watching on dashboard")
    cw_playa = CW_players.objects.filter(user=request.user)
    return render(request,'main/index.html', {'cw_playa':cw_playa})

class ChwCreateView(CreateView):    
    template_name = 'main/create.html'
    form_class = ChwForm
    success_url = reverse_lazy('mainapp:main')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@api_view(['GET'])
@login_required
def update_qr_and_auth(request):
    response = auth_new_player()
    logger.info(f"{request.user.username} get response from auth new player")
    if response["status"] == "success":
        logger.success(f"{request.user.username} authed via QR and got {response['session']=}")
        return JsonResponse({"session_string":response["session"]},status=200)
    return JsonResponse({"status":response["status"]}, status=response["status_code"])

@api_view(["GET"])
@login_required
def give_qr_img(request):
    tg_url = redis.get("QR_LOGIN_TEXT")
    tg_url = tg_url.decode("utf-8")
    logger.info(f"[+] TELEGRAM LOGIN URL: {tg_url}")
    context = {"qr":tg_url}
    return render(request,'main/qr.html', context)
