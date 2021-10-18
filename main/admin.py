from django.contrib import admin
from .models import CW_players

class ChAdmin(admin.ModelAdmin):
    list_display = ('chw_username','username','status','player_class', 'session','send_report','registration_date')
    list_display_links = ('chw_username','username','registration_date')
    search_fields = ('chw_username','username','status','player_class',)

admin.site.register(CW_players,ChAdmin)
