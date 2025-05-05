from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, Http404

from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from fitApp.forms import LoginForm, RegisterForm, SportForm, SoccerForm, TennisForm, RunningForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fitApp.models import AnalysisRun



import re
import os
import uuid
import traceback

from video_analysis.types import Joint
from video_analysis.run_analysis import run_analysis
from video_analysis.sports import ALL_SPORTS


def login_action(request):

    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'fitApp/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'fitApp/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'fitApp/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'fitApp/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def home(request):
    return render(request, 'fitApp/welcome_page.html')


@login_required
def profile(request):
    sport_form = SportForm()
    technique_form = None
    show_technique = False
    user_runs = AnalysisRun.objects.filter(user=request.user).order_by('-id')

    if request.method == 'POST':
        sport_form = SportForm(request.POST)
        selected_sport = request.POST.get('sport')
        selected_technique = request.POST.get('technique')

        if sport_form.is_valid():
            user_runs = user_runs.filter(sport=selected_sport)
            show_technique = True

            if selected_sport == 'soccer':
                technique_form = SoccerForm(request.POST)
            elif selected_sport == 'tennis':
                technique_form = TennisForm(request.POST)
            elif selected_sport == 'running':
                technique_form = RunningForm(request.POST)

            if technique_form and technique_form.is_valid():
                user_runs = user_runs.filter(technique=selected_technique)

    return render(request, 'fitApp/profile.html', {
        'runs': user_runs,
        'sport_form': sport_form,
        'technique_form': technique_form,
        'show_technique': show_technique
    })




@login_required
def past_run(request,run_id):
    run = get_object_or_404(AnalysisRun, id=run_id, user=request.user)
    return render(request, 'fitApp/analysis_run_detail.html', {'run': run})



@login_required
def pick_sport(request):
    if request.method == 'GET':
        context = {'sports': ALL_SPORTS.values()}
        return render(request, 'fitApp/pick_sport.html', context)

@login_required
def pick_technique(request):
    if request.method == 'POST':
        sport_key = request.POST.get('sport') 
        sport = ALL_SPORTS.get(sport_key)
        request.session['sport'] = sport.key
        context = {
            'sport': sport,
            'techniques': sport.techniques
        }
        return render(request, 'fitApp/pick_technique.html', context)

@login_required
def display_upload_form(request):
    request.session['technique'] = request.POST.get("technique")
    if request.method == 'POST':
        context = {
            'sport': request.session.get('sport'),
            'technique': request.session.get('technique')
        }
        return render(request, 'fitApp/upload_videos.html', context)
    return render(request, 'fitApp/upload_videos.html')

def convert_markdown(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)



@login_required
def analyze_videos(request):
    if request.method == 'POST':
        user_video = request.FILES.get('user_video')
        athlete_video = request.FILES.get('athlete_video')

        if not user_video or not athlete_video:
            return render(request, 'fitApp/upload_videos.html', {
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
            return render(request, 'fitApp/upload_videos.html', {
                'error': f"Something went wrong: {str(e)}"
            })

        joint_labels = {joint: joint.replace("_", " ").title() for joint in results['angle_plots'].keys()}

        run = AnalysisRun(
            video= results['comp_image'],
            feedback=convert_markdown(results['llm_feedback']),
            sport=request.session['sport'],
            technique=request.session['technique'],
            user=request.user
        )
        run.save()

        print("RESULULTS CALCULATED AND RUN SAVED")
        return render(request, 'fitApp/results.html', {
            'user_image_url': default_storage.url(results['user_image']),
            'athlete_image_url': default_storage.url(results['comp_image']),
            'llm_feedback': convert_markdown(results['llm_feedback']),
            'angle_plots': {k: default_storage.url(v) for k, v in results['angle_plots'].items()},
            # 'aligned_plots': {k: default_storage.url(v) for k, v in results['aligned_plots'].items()},
            # 'dtw_plots': {k: default_storage.url(v) for k, v in results['dtw_plots'].items()},
            'joint_labels': joint_labels,
        })


    return render(request, 'fitApp/upload_videos.html')

