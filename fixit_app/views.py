from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.shortcuts import render
from datetime import datetime
import openai
from django.conf import settings
from django.http import JsonResponse


openai.api_key = settings.OPENAI_API_KEY
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def ask_ai(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        try:
            answer = get_simple_answer(user_input)
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def get_simple_answer(user_question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that explains technical things in simple, friendly terms for elderly users."
            },
            {
                "role": "user",
                "content": user_question
            }
        ],
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()


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