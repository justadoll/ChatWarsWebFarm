from django.contrib import admin
from .models import CW_players

@admin.action(description="Уложить игроков спать")
def nonactive(modeladmin, request, queryset):
    queryset.update(status='🛌Sleep')

class ChAdmin(admin.ModelAdmin):
    list_display = ('user','chw_username','username','status','player_class', 'lvl', 'phone_number', 'send_report','registration_date')
    list_display_links = ('chw_username','username')
    search_fields = ('user','chw_username','username','status','player_class',)
    actions = [nonactive]

admin.site.register(CW_players,ChAdmin)
