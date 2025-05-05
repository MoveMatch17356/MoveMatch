from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import HttpResponseBadRequest

import re
import os
import uuid
import traceback

from video_analysis.types import Joint
from video_analysis.run_analysis import run_analysis
from video_analysis.sports import ALL_SPORTS
from .models import ReferenceVideo

def home(request):
    return render(request, 'welcome_page.html')

def pick_sport(request):
    if request.method == 'GET':
        context = {'sports': ALL_SPORTS.values()}
        return render(request, 'pick_sport.html', context)

def pick_technique(request):
    if request.method == 'POST':
        sport_key = request.POST.get('sport')
        sport = ALL_SPORTS.get(sport_key)

        if not sport:
            return HttpResponseBadRequest("Invalid or missing sport.")

        request.session['sport'] = sport.key  # store for use later

        context = {
            'sport': sport,
            'techniques': sport.techniques
        }
        return render(request, 'pick_technique.html', context)

def display_upload_form(request):
    if request.method == 'POST':
        technique_key = request.POST.get('technique')
        sport_key = request.session.get('sport')
        sport = ALL_SPORTS.get(sport_key)
        technique = None

        if sport:
            technique = next((t for t in sport.techniques if t.key == technique_key), None)

        if not sport or not technique:
            return HttpResponseBadRequest("Missing or invalid sport or technique.")
        
        request.session['technique'] = technique_key

        context = {
            'sport': sport,
            'technique': technique,
        }
        return render(request, 'upload_videos.html', context)

def convert_markdown(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def analyze_videos(request):
    if request.method == 'POST':
        user_video = request.FILES.get('user_video')
        athlete_video = request.FILES.get('athlete_video')
        selected_library_video = request.POST.get('selected_library_video')
        reference_option = request.POST.get('reference_option')

        # --- 1. Validate user upload ---
        if not user_video:
            return render(request, 'upload_videos.html', {
                'error': 'Please upload your own video.'
            })

        user_path = default_storage.save(f'tmp/user_{uuid.uuid4()}.mp4', user_video)

        if selected_library_video:
            # Convert URL path to absolute file path
            relative_path = selected_library_video.replace(settings.MEDIA_URL, "")
            athlete_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        # --- 2. Handle reference video logic based on selection ---
        if reference_option == "upload":
            if not athlete_video:
                return HttpResponseBadRequest("You selected to upload a reference video but did not provide one.")
            athlete_path = default_storage.save(f'tmp/athlete_{uuid.uuid4()}.mp4', athlete_video)

        elif reference_option == "library":
            if not selected_library_video or not selected_library_video.strip():
                return HttpResponseBadRequest("You selected a library video but did not choose one.")
            relative_path = selected_library_video.replace(settings.MEDIA_URL, "")
            athlete_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        else:
            return HttpResponseBadRequest("Invalid reference video option.")

        # --- 3. Build absolute paths ---
        abs_user_path = os.path.join(settings.MEDIA_ROOT, user_path)
        abs_athlete_path = athlete_path
        if not athlete_path.startswith("/media"):
            abs_athlete_path = os.path.join(settings.MEDIA_ROOT, athlete_path)

        # --- 4. Run analysis ---
        try:
            sport_key = request.session.get('sport')
            technique_key = request.session.get('technique')
            sport = ALL_SPORTS.get(sport_key)
            technique = next((t for t in sport.techniques if t.key == technique_key), None)

            if not sport or not technique:
                raise ValueError("Missing sport or technique information in session.")

            results = run_analysis(
                sport=sport.label,
                technique=technique.label,
                movement_key=technique.key,
                user_path=abs_user_path,
                comp_path=abs_athlete_path,
                selected_joints=technique.joints
            )

        except Exception as e:
            traceback.print_exc()
            return render(request, 'upload_videos.html', {
                'error': f"Something went wrong: {str(e)}"
            })

        # --- 5. Render results ---
        joint_labels = {joint: joint.replace("_", " ").title() for joint in results['angle_plots'].keys()}
        return render(request, 'results.html', {
            'user_image_url': default_storage.url(results['user_image']),
            'athlete_image_url': default_storage.url(results['comp_image']),
            'llm_feedback': convert_markdown(results['llm_feedback']),
            'angle_plots': {k: default_storage.url(v) for k, v in results['angle_plots'].items()},
            'joint_labels': joint_labels,
        })


def athlete_library(request):
    sport = request.GET.get('sport')
    technique = request.GET.get('technique')
    user_video_path = request.GET.get('user_video_path')

    if not sport or not technique:
        return HttpResponseBadRequest("Missing sport or technique.")

    # Pull from DB model instead of scanning folders
    videos = ReferenceVideo.objects.filter(sport=sport, technique=technique)

    return render(request, 'athlete_library.html', {
        'sport': {'key': sport, 'label': sport.capitalize()},
        'technique': {'key': technique, 'label': technique.capitalize()},
        'athlete_videos': videos,
        'user_video_path': user_video_path
    })