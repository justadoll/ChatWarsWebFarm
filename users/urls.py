from django.urls import path

from .views import register, user_router
urlpatterns = [ 
    path('', user_router, name="router"),
    path('registration/', register, name="register")
    ]