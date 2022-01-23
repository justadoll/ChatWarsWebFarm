from django.db import models
from django.contrib.auth.models import User


class CW_players(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="new_spending", null=True)
    chw_username=models.CharField(max_length=32)
    username=models.CharField(max_length=32,blank=True,null=True)
    phone_number=models.CharField(max_length=13,blank=True)
    session=models.CharField(max_length=355)
    status=models.CharField(max_length=50,blank=True)
    player_class=models.CharField(max_length=15,blank=True)
    defcow=models.CharField(max_length=36,blank=True)
    lvl = models.IntegerField(blank=True,null=True)
    send_report=models.CharField(max_length=32,blank=True)
    registration_date=models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        verbose_name_plural="Игроки"
        verbose_name="игрока"
        ordering=['-registration_date']
