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
        request.session['sport'] = sport.key
        context = {
            'sport': sport,
            'techniques': sport.techniques
        }
        return render(request, 'pick_technique.html', context)

def display_upload_form(request):
    request.session['technique'] = request.POST.get("technique")
    if request.method == 'POST':
        context = {
            'sport': request.session.get('sport'),
            'technique': request.session.get('technique')
        }
        return render(request, 'upload_videos.html', context)
    return render(request, 'upload_videos.html')

def convert_markdown(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def analyze_videos(request):
    if request.method == 'POST':
        user_video = request.FILES.get('user_video')
        athlete_video = request.FILES.get('athlete_video')

        if not user_video or not athlete_video:
            return render(request, 'upload_videos.html', {
                'error': 'Please upload both videos for analysis.'
            })

        user_path = default_storage.save(f'tmp/user_{uuid.uuid4()}.mp4', user_video)
        athlete_path = default_storage.save(f'tmp/athlete_{uuid.uuid4()}.mp4', athlete_video)

        abs_user_path = os.path.join(settings.MEDIA_ROOT, user_path)
        abs_athlete_path = os.path.join(settings.MEDIA_ROOT, athlete_path)

        try:
            sport_key = request.session.get('sport')
            technique_key = request.session.get('technique')
            sport = ALL_SPORTS.get(sport_key)
            technique = next((t for t in sport.techniques if t.key == technique_key), None)

            if not sport or not technique:
                raise ValueError("Missing sport or technique information in session.")

            selected_joints = technique.joints

            results = run_analysis(
                sport=sport.label,
                technique=technique.label,
                movement_key=technique.key,
                user_path=abs_user_path,
                comp_path=abs_athlete_path,
                selected_joints=selected_joints
            )

        except Exception as e:
            print("Error during analysis:")
            traceback.print_exc()
            return render(request, 'upload_videos.html', {
                'error': f"Something went wrong: {str(e)}"
            })

        joint_labels = {joint: joint.replace("_", " ").title() for joint in results['angle_plots'].keys()}

        return render(request, 'results.html', {
            'user_image_url': default_storage.url(results['user_image']),
            'athlete_image_url': default_storage.url(results['comp_image']),
            'llm_feedback': convert_markdown(results['llm_feedback']),
            'angle_plots': {k: default_storage.url(v) for k, v in results['angle_plots'].items()},
            # 'aligned_plots': {k: default_storage.url(v) for k, v in results['aligned_plots'].items()},
            # 'dtw_plots': {k: default_storage.url(v) for k, v in results['dtw_plots'].items()},
            'joint_labels': joint_labels,
        })


    return render(request, 'upload_videos.html')

def athlete_library(request):
    sport = request.GET.get('sport')
    technique = request.GET.get('technique')
    user_video_path = request.GET.get('user_video_path')  # optional if you want to pass it here

    if not sport or not technique:
        return HttpResponseBadRequest("Missing sport or technique.")

    # This is where you'd get real data from a DB or storage
    reference_dir = os.path.join(settings.MEDIA_ROOT, 'athlete_library', sport, technique)
    if not os.path.exists(reference_dir):
        videos = []
    else:
        videos = [
            {
                'path': os.path.join('athlete_library', sport, technique, fname),
                'url': os.path.join(settings.MEDIA_URL, 'athlete_library', sport, technique, fname)
            }
            for fname in os.listdir(reference_dir)
            if fname.endswith('.mp4')
        ]

    return render(request, 'athlete_library.html', {
        'sport': {'key': sport, 'label': sport.capitalize()},
        'technique': {'key': technique, 'label': technique.capitalize()},
        'athlete_videos': videos,
        'user_video_path': user_video_path
    })