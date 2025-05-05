"""
URL configuration for MoveMatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from fitApp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/login/', views.login_action, name='login'),
    path('logout/', views.logout_action, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('analysis/<int:run_id>/', views.past_run, name = 'past_run'),
    path('accounts/register/', views.register_action, name='register'),
    path('pick_sport/', views.pick_sport, name ='pick_sport'),
    path('pick_technique/', views.pick_technique, name ='pick_technique'),
    path('display_upload_form/', views.display_upload_form, name = 'display_upload_form'),
    path('analyze_videos/', views.analyze_videos, name='analyze_videos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
