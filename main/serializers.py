from rest_framework import serializers
from main.models import CW_players

#https://www.django-rest-framework.org/api-guide/serializers/

class PlayerSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(PlayerSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = CW_players
        fields = ['id', 'chw_username', 'username', 'status', 'player_class', 'session']
        read_only_fields = ['id', 'chw_username', 'username', 'session']
