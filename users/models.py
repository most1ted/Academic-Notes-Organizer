from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    count = models.IntegerField(default=0,null=True,blank=True)
