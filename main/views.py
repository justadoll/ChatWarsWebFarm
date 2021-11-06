from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.conf import settings
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import CW_players
from .serializers import PlayerSerializer
from .forms import ChwForm
from loguru import logger

from .chw_manager import ChwMaster
import asyncio
from channels.db import database_sync_to_async

chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)

def chw_manager(action, id, button):
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
        async_result = loop.run_until_complete(chw_master.mainQuestRun(player, button))
        logger.debug(async_result)
        loop.close()
        player.status="🛌Sleep"
        player.save()
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
                #dct_data = serializer.data.__dict__
                #user_data_request = dct_data['serializer'].data # geting data from user request with valid fields
                #logger.debug(user_data_request)
                for test in serializer:
                    if test.value == "Run":
                        logger.debug("Run, forest, run!")
                        chw_manager("quest_run", player.pk, button2int[str_button])

                        #logger.info(chw_manager("get_game_time", player.pk))
                        #logger.info(chw_manager("get_user_data", player.pk))

                        return JsonResponse(serializer.data)
                    else:
                        pass
                return JsonResponse({"response":"Something gone wrong"}, status=401)
        return JsonResponse(serializer.errors, status=400)


def index(request):
    cw_playa = CW_players.objects.order_by('-registration_date')
    return render(request,'main/index.html', {'cw_playa':cw_playa})

class ChwCreateView(CreateView):
    template_name = 'main/create.html'
    form_class = ChwForm
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

@api_view(['POST'])
def send_phone_request(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            logger.debug(data)
            return JsonResponse({"status":"send"}, status=200)
        except Exception as e:
            return JsonResponse({"status":"something gone wrong"}, status=400)