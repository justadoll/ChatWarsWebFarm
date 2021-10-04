from rest_framework import serializers
from .models import CW_players

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CW_players
        fields = ('id','chw_username', 'username', 'status', 'player_class')
