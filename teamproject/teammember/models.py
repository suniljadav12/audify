from django.db import models

class AudioFile(models.Model):
    audio = models.FileField(upload_to='audio/')
    subtitles = models.TextField()

    def __str__(self):
        return self.audio.name

# Create your models here.
