from django.db import models


class Book(models.Model):
    class Cover(models.IntegerChoices):
        SOFT = 0
        HARD = 1
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.IntegerField(choices=Cover)
    inventory = models.IntegerField(default=0)
    fee = models.IntegerField()


