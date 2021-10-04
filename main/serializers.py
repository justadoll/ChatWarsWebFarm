from rest_framework import serializers
from main.models import CW_players

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CW_players
        fields = ['id', 'chw_username', 'username', 'status', 'player_class']
