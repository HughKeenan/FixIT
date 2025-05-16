from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.shortcuts import render
from datetime import datetime
import openai
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages as msg
from django.shortcuts import get_object_or_404, redirect
from .models import Message
from django.views.decorators.csrf import csrf_exempt

openai.api_key = settings.OPENAI_API_KEY
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
@csrf_exempt
def ask_ai(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        resend = request.POST.get('resend') == 'true'

        if not user_input:
            return redirect('home')
        
        try:
            answer = get_simple_answer(user_input)

            # Save to session to show on homepage
            request.session['last_question'] = user_input
            request.session['last_response'] = answer

            Message.objects.create(user=request.user, question=user_input, response=answer)

            if resend:
                return redirect('home')

            return JsonResponse({'answer': answer})

        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            else:
                return redirect('home')

    return JsonResponse({'answer': answer})



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


@login_required
def message_history(request):
    messages = Message.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'messages': messages})

@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk, user=request.user)
    message.delete()
    msg.success(request, "Message deleted.")
    return redirect('history')

@login_required
def clear_history(request):
    Message.objects.filter(user=request.user).delete()
    msg.success(request, "All history cleared.")
    return redirect('history')

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
    context = {'year': datetime.now().year, 'messages': []}
    if request.user.is_authenticated:
        messages = Message.objects.filter(user=request.user).order_by('created_at')
        context['last_question'] = request.session.pop('last_question', None)
        context['last_response'] = request.session.pop('last_response', None)
        context['messages'] = messages
    
    return render(request, 'home.html', context)