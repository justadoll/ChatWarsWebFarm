from django.shortcuts import render, redirect

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings

logger = settings.LOGGER

def user_router(request):
    if request.user.is_authenticated:
        return redirect("mainapp:main")
    else:
        return redirect("dj_managment_app:login")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('mainapp:main')

    else:
        form = UserCreationForm()
    
    context = {'form':form}
    return render(request, 'registration/register.html', context)
