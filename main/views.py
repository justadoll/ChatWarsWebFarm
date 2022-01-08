from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.conf import settings
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .tasks import make_qr_login
from .serializers import PlayerSerializer
from .forms import ChwForm

from .chw_manager import ChwMaster
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
import asyncio

logger = settings.LOGGER
chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)

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
    if action == "get_user_data":#TODO POST create and insert info to new chatWarsPlayers table
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

@api_view(['GET','POST'])
def players_list(request):
    if request.method == 'GET':
        players = CW_players.objects.all()
        serializer = PlayerSerializer(players, fields=('id','chw_username','status','player_class'), many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        logger.debug("POST REQUEST TO CREATE ACCOUNT!")
        logger.debug(f"{data=}")
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET','PUT','DELETE'])
def indiv_player(request,pk):
    try:
        player = CW_players.objects.get(pk=pk)
    except CW_players.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PlayerSerializer(player,fields=('id','chw_username','username','status','player_class'))
        new_data = chw_manager("get_info", player.pk)
        if not new_data:
            context = {"status": "Player logouted!"}
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
        return render(request, 'main/player.html', context)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        button2int = {"forest": 0, "swamp": 1, "mount": 2, "cow": 3}
        str_button = data['quest']
        logger.debug(f"{button2int[str_button]=}")
        if(player.status=="Run"):
            logger.debug("Already run!")
            return JsonResponse({"response":"Player already run!"}, status=208)
        else:
            serializer = PlayerSerializer(player, data=data, fields=('id','status'))
            if serializer.is_valid():
                serializer.save()
                logger.debug(f"{player.chw_username} Run, forest, run!")
                chw_manager("quest_run", player.pk, button2int[str_button])
                return JsonResponse(serializer.data)
            else:
                logger.error(f"{serializer.errors=}")
                return JsonResponse({"response":"Something gone wrong"}, status=401)
    elif request.method == "DELETE":
        try:
            player.delete()
        except Exception as e:
            logger.erroe(f"{e=}")
            return JsonResponse({"status":"Something gone wrong!"}, status=400)
        else:
            return JsonResponse({"status":"OK"}, status=200)

@api_view(['PUT'])
def send_command(request, pk:int):
    logger.debug(f"{pk=}")
    data = JSONParser().parse(request)
    logger.debug(f"{data=}")
    player = CW_players.objects.get(pk=pk)
    response = chw_manager(action="chat_shell", id=player.pk, command=data['command'])
    logger.debug(f"{response=}")
    
    return JsonResponse({"result":response}, status=200)

def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})

class ChwCreateView(CreateView):
    template_name = 'main/create.html'
    form_class = ChwForm
    success_url = reverse_lazy('mainapp:main')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


@api_view(['GET'])
def update_qr_and_auth(request):
    response = auth_new_player()
    logger.info(f"{response=}")
    if response["status"] == "success":
        return JsonResponse({"session_string":response["session"]},status=200)
    return JsonResponse({"status":response["status"]}, status=response["status_code"])

@api_view(["GET"])
def give_qr_img(request):
    context = {"qr":settings.QR_LOGIN_TEXT}
    return render(request,'main/qr.html', context)