from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Registrator v.0.1
# User inputs his creds for telegram auth, after success - making request to my server API with encoded user-data (dont forget about username in request)
# API decode data, save it to DB with Status 'New' and player class 'Unknown'
# Dashboard updates, we see a new user and telegram app makes 'update' request from this session to get info about player

with TelegramClient(StringSession(), 2299164, "c8b6a3a2edaae9f1d98a2c5596457dce") as client:
        string = client.session.save()
        print(string)
