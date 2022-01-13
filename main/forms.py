from django.forms import ModelForm
from .models import CW_players

class ChwForm(ModelForm):
    #extra_field = CharField(widget=HiddenInput())
    class Meta:
        model = CW_players
        fields = ['chw_username','session']