from django.db import models

# Create your models here.


class Movie(models.Model):
    image_url = models.CharField(max_length=256)
    movie_url = models.CharField(max_length=256)
    title = models.CharField(max_length=128)
    number = models.CharField(max_length=16)
    date = models.DateTimeField()

    def abbreviated_title(self):
        if len(self.title) <= 40:
            return self.title
        else:
            return self.title[:40] + '...'
