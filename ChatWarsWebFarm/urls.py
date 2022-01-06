from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('main/',include(('main.urls',"main"), namespace="mainapp")),
    path('admin/', admin.site.urls),
]
