from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('',include(('users.urls',"users"), namespace="usersapp")),
    path('accounts/',include(('django.contrib.auth.urls','dj_managment'),namespace="dj_managment_app")),
    path('main/',include(('main.urls',"main"), namespace="mainapp")),
    path('admin/', admin.site.urls),
]
