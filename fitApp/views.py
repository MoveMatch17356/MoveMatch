from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings

import re
import os
import uuid
import traceback

from video_analysis.types import Joint
from video_analysis.run_analysis import run_analysis
from video_analysis.sports import ALL_SPORTS

import shutil

def clear_tmp_media():
    tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    if os.path.exists(tmp_dir):
        for filename in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

import subprocess

def convert_to_mp4(input_path):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_relpath = f'tmp/{base_name}_converted.mp4'
    output_path = os.path.join(settings.MEDIA_ROOT, output_relpath)

    subprocess.run([
        'ffmpeg', '-y', '-i', input_path,
        '-vcodec', 'libx264', '-acodec', 'aac',
        '-preset', 'fast', output_path
    ], check=True)

    return output_relpath  # return relative path so it can be used with default_storage.url(...)

def home(request):
    # clear tmp folder
    clear_tmp_media()
    # render page
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

# def display_upload_form(request):
#     request.session['technique'] = request.POST.get("technique")
#     if request.method == 'POST':
#         context = {
#             'sport': request.session.get('sport'),
#             'technique': request.session.get('technique')
#         }
#         return render(request, 'upload_videos.html', context)
#     return render(request, 'upload_videos.html')

def display_upload_form(request):
    if request.method == 'POST':
        request.session['technique'] = request.POST.get("technique")

        user_video = request.FILES.get("user_video")
        athlete_video = request.FILES.get("athlete_video")

        user_video_url = None
        athlete_video_url = None

        if user_video and athlete_video:
            user_path = default_storage.save(f'tmp/user_{uuid.uuid4()}.mp4', user_video)
            athlete_path = default_storage.save(f'tmp/athlete_{uuid.uuid4()}.mp4', athlete_video)

            abs_user_path = os.path.join(settings.MEDIA_ROOT, user_path)
            abs_athlete_path = os.path.join(settings.MEDIA_ROOT, athlete_path)

            abs_user_path = convert_to_mp4(abs_user_path)
            abs_athlete_path = convert_to_mp4(abs_athlete_path)

            user_video_url = default_storage.url(os.path.relpath(abs_user_path, settings.MEDIA_ROOT))
            athlete_video_url = default_storage.url(os.path.relpath(abs_athlete_path, settings.MEDIA_ROOT))

        context = {
            'sport': request.session.get('sport'),
            'technique': request.session.get('technique'),
            'user_video_url': user_video_url,
            'athlete_video_url': athlete_video_url
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

        # # Convert and get relative paths
        # user_path = convert_to_mp4(abs_user_path)
        # athlete_path = convert_to_mp4(abs_athlete_path)

        # abs_user_path = os.path.join(settings.MEDIA_ROOT, user_path)
        # abs_athlete_path = os.path.join(settings.MEDIA_ROOT, athlete_path)

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
                user_video_path=abs_user_path,
                comp_video_path=abs_athlete_path,
                selected_joints=selected_joints
            )

            # 🔍 Debug: Print plot paths
            print("Angle plots:")
            for k, v in results['angle_plots'].items():
                print(f"  {k}: {v}")
            print("Aligned plots:")
            for k, v in results['aligned_plots'].items():
                print(f"  {k}: {v}")
            print("DTW plots:")
            for k, v in results['dtw_plots'].items():
                print(f"  {k}: {v}")

        except Exception as e:
            print("Error during analysis:")
            traceback.print_exc()
            return render(request, 'upload_videos.html', {
                'error': f"Something went wrong: {str(e)}"
            })

        joint_labels = {joint: joint.replace("_", " ").title() for joint in results['angle_plots'].keys()}

        return render(request, 'results.html', {
            'user_video_url': default_storage.url(user_path),
            'athlete_video_url': default_storage.url(athlete_path),
            # 'user_image_url': default_storage.url(results['user_image']),
            'user_image_url': '/' + results['user_image'],
            # 'athlete_image_url': default_storage.url(results['comp_image']),
            'athlete_image_url': '/' + results['comp_image'],
            'llm_feedback': convert_markdown(results['llm_feedback']),
            # 'angle_plots': {k: default_storage.url(v) for k, v in results['angle_plots'].items()},
            'angle_plots': {k: '/' + v for k, v in results['angle_plots'].items()},
            'joint_labels': joint_labels,
        })

    return render(request, 'upload_videos.html')