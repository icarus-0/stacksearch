from django.db import models
from django.contrib.auth.models import User
from django.http import response
# Create your models here.


class searchedData(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=30)
    search = models.TextField()
    response = models.JSONField()
    time = models.CharField(max_length=50)
