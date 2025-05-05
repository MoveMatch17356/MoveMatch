from django.db import models

class ReferenceVideo(models.Model):
    sport = models.CharField(max_length=50)
    technique = models.CharField(max_length=50)
    title = models.CharField(max_length=100, blank=True)
    video = models.FileField(upload_to='athlete_library/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or self.video.name} ({self.sport} - {self.technique})"
from django.contrib.auth.models import User



class AnalysisRun (models.Model):
    feedback = models.CharField(max_length = 200)
    sport = models.CharField(max_length = 50)
    technique = models.CharField(max_length = 50)
    user = models.ForeignKey(User , on_delete =models.PROTECT )
    uploaded_at = models.DateTimeField(auto_now_add=True) 
    title = models.CharField(max_length=100, blank=True)
    video = models.FileField(upload_to='video/', max_length=200)
   
   
    