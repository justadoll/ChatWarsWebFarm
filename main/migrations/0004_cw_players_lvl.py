# Generated by Django 3.2.9 on 2021-12-05 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_cw_players_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='cw_players',
            name='lvl',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]