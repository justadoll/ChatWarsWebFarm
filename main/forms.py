from django.forms import ModelForm
from .models import CW_players

class ChwForm(ModelForm):
    class Meta:
        model = CW_players
        fields = ('username','phone_number')