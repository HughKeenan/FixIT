from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.shortcuts import render
from datetime import datetime

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # change 'home' to your actual view name
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
    return render(request, 'registration/login.html', {'form': form})

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})