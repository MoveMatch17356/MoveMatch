from django.db import models

class ReferenceVideo(models.Model):
    sport = models.CharField(max_length=50)
    technique = models.CharField(max_length=50)
    title = models.CharField(max_length=100, blank=True)
    video = models.FileField(upload_to='athlete_library/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or self.video.name} ({self.sport} - {self.technique})"