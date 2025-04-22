from django import forms

SPORT_CHOICES = [
    ('soccer', 'Soccer'),
    ('tennis', 'Tennis'),
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


    


    
