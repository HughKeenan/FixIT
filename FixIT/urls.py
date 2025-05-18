"""
URL configuration for FixIT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from fixit_app import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('ask-ai/', views.ask_ai, name='ask_ai'),
    path('history/', views.message_history, name='history'),
    path('history/delete/<int:pk>/', views.delete_message, name='delete_message'),
    path('history/clear/', views.clear_history, name='clear_history'),
    path('about/', views.about, name='about'),
    path('meet-the-team/', views.meet_the_team, name='meet_the_team'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('contact/', views.contact, name='contact'),
]
