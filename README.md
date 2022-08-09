# ChatWarsWebFarm (CWWF)

## Installation 

### 1) Install python:
 * `sudo apt install python3 python3-pip libpq-dev python3-dev`
### 2) Install libs:
 * `pip3 install -r requirements.txt`
### 3) Edit `.env.dist` and rename it to `.env`:
 * Create/get api keys from https://my.telegram.org/apps
### 4) Make migrations:
 * `python manage.py makemigrations`
 * `python manage.py migrate`
### 5) Run server:
 * If you running in vpn/localhost - add `ALLOWED_HOSTS` IPS to `ChatWarsWebFarm/settings.py`
 * `python manage.py runserver 0.0.0.0:8080`

PoC:
![Player](https://github.com/justadoll/ChatWarsWebFarm/blob/main/git_pics/1.jpg?raw=true)

![TG Player](https://github.com/justadoll/ChatWarsWebFarm/blob/main/git_pics/2.jpg?raw=true)

![Run funcs](https://github.com/justadoll/ChatWarsWebFarm/blob/main/git_pics/3.jpg?raw=true)

![Running](https://github.com/justadoll/ChatWarsWebFarm/blob/main/git_pics/4.jpg?raw=true)

![TG Running](https://github.com/justadoll/ChatWarsWebFarm/blob/main/git_pics/5.jpg?raw=true)

![](https://komarev.com/ghpvc/?username=ChatWarsWebFarm&color=green&label=Views)
