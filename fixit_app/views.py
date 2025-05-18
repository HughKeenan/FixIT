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
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils.timezone import localtime
import textwrap
import re

openai.api_key = settings.OPENAI_API_KEY
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def ask_ai(request):
    print(request)
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        resend = request.POST.get('resend') == 'true'

        if not user_input:
            return redirect('home')

        try:
            answer = get_simple_answer(user_input)
            formatted_answer = fix_markdown_formatting(answer)

            # Save to session for display on homepage
            request.session['last_question'] = user_input
            request.session['last_response'] = formatted_answer

            # Save to DB only if user is logged in
            if request.user.is_authenticated:
                Message.objects.create(
                    user=request.user,
                    question=user_input,
                    response=formatted_answer
                )
            
            if resend:
                return redirect('home')

            return JsonResponse({'answer': formatted_answer})

        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            else:
                return redirect('home')

    # Handle non-POST requests gracefully
    return JsonResponse({'error': 'Invalid request method'}, status=405)



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

def fix_markdown_formatting(text):
    """
    Clean and convert AI text response into proper Markdown format.
    """
    # Convert lines like '### Ingredients:' into headings on new lines
    text = re.sub(r'###\s*(.+?):', r'\n### \1\n', text)

    # Ensure numbered steps are on their own line
    text = re.sub(r'(\d\.)\s*•?\s*\*\*(.+?)\*\*', r'\n\1 **\2**', text)

    # Fix any bullet misuse: • becomes -
    text = text.replace('•', '-')

    # Fix double dashes
    text = text.replace('--', '—')

    return text.strip()

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

def generate_pdf(request):
    # Get the logged-in user and their associated messages
    user = request.user
    messages = Message.objects.filter(user=user).order_by('-created_at')  # Get messages for the logged-in user
    
    # Create a response object with the content type for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_posts.pdf"'

    # Create a PDF object using the response as the output
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Set up title and styling
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, f"Posts by {user.username}")
    
    pdf.setFont("Helvetica", 12)

    # Set the starting position for the messages
    y_position = height - 80
    line_height = 14
    max_line_width = width - 100  # Adjust this based on where you want the text to start on the page

    # Add each message to the PDF
    for message in messages:
        if y_position < 50:  # If we reach the bottom of the page, create a new page
            pdf.showPage()
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, height - 50, f"Posts by {user.username}")
            pdf.setFont("Helvetica", 12)
            y_position = height - 80  # Reset the starting position for the new page
        
        # Display the question with wrapping
        time_posted = localtime(message.created_at).strftime('%Y-%m-%d %H:%M:%S')
        question_text = f"Question from {time_posted}: {message.question}"
        
        # Wrap the text for the question
        wrapped_question = textwrap.fill(question_text, width=80)  # Wrap text to fit the page width
        
        # Add the wrapped question to the PDF, line by line
        for line in wrapped_question.splitlines():
            pdf.drawString(100, y_position, line)
            y_position -= line_height
        
        # If there's a response, add it to the PDF as well
        if message.response:
            response_text = f"Response: {message.response}"
            wrapped_response = textwrap.fill(response_text, width=80)  # Wrap the response text
            
            # Add the wrapped response to the PDF, line by line
            for line in wrapped_response.splitlines():
                pdf.drawString(100, y_position, line)
                y_position -= line_height
        
        # Add space between messages
        y_position -= 10

    # Finalize and save the PDF
    pdf.showPage()
    pdf.save()

    return response

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

def about(request):
    context = {'year': datetime.now().year}

    if request.user.is_authenticated:
        context['last_question'] = request.session.pop('last_question', None)
        context['last_response'] = request.session.pop('last_response', None)

    return render(request, 'about.html', context)

def contact(request):
    context = {'year': datetime.now().year}

    if request.user.is_authenticated:
        context['last_question'] = request.session.pop('last_question', None)
        context['last_response'] = request.session.pop('last_response', None)

    return render(request, 'contact.html', context)

def privacy(request):
    context = {'year': datetime.now().year}

    if request.user.is_authenticated:
        context['last_question'] = request.session.pop('last_question', None)
        context['last_response'] = request.session.pop('last_response', None)

    return render(request, 'privacy.html', context)

def meet_the_team(request):
    context = {
        'title': 'Meet the Team',  # Example data
        # Add any other data you want to pass to the template
    }
    return render(request, 'meet_the_team.html', context)
