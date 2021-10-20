from django.db import models

class CW_players(models.Model):
    chw_username=models.CharField(max_length=32)
    username=models.CharField(max_length=32,blank=True,null=True)
    session=models.CharField(max_length=355)
    status=models.CharField(max_length=50)
    player_class=models.CharField(max_length=10) #could add foreign key for sorting class
    send_report=models.CharField(max_length=32,blank=True)
    registration_date=models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        verbose_name_plural="Игроки"
        verbose_name="игрока"
        ordering=['-registration_date']
