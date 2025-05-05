from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


SPORT_CHOICES = [
    ('tennis', 'Tennis'),
    ('soccer', 'Soccer'),
    ('running', 'Running'),
]

SOCCER_TECHNIQUES = [
    ('passing', 'Passing'),
    ('shooting', 'Shooting'),
    ('dribbling', 'Dribbling'),
]

TENNIS_TECHNIQUES = [
    ('slice', 'Slice'),
    ('serve', 'Serve'),
    ('volley', 'Volley'),
]

RUNNING_TECHNQIUES = [
    ('sprinting', 'Sprinting'),
    ('posture', 'Posture')
]

class SportForm(forms.Form):
    sport = forms.ChoiceField(choices=SPORT_CHOICES, label='Choose a Sport')

class SoccerForm(forms.Form):
    technique = forms.ChoiceField(choices=SOCCER_TECHNIQUES, label='Choose a Soccer Technique')

class TennisForm(forms.Form):
    technique = forms.ChoiceField(choices=TENNIS_TECHNIQUES, label='Choose a Tennis Technique')

class RunningForm(forms.Form):
    technique = forms.ChoiceField(choices=RUNNING_TECHNQIUES, label='Choose a Running Technique')
    
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        
    )
    password = forms.CharField(
        max_length=200,
        
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return cleaned_data

    
class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length=20)
    password  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput())
    confirm_password  = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username
