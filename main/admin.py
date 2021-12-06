from django.contrib import admin
from .models import CW_players

class ChAdmin(admin.ModelAdmin):
    list_display = ('chw_username','username','status','player_class', 'lvl', 'phone_number', 'send_report','registration_date')
    list_display_links = ('chw_username','username')
    search_fields = ('chw_username','username','status','player_class',)

admin.site.register(CW_players,ChAdmin)
