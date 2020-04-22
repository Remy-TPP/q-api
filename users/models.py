from django.db import models
from django.conf import settings


class UserType(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return '%s' % (self.name)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    usertypes = models.ManyToManyField(UserType, related_name='users')
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return '%s' % (self.user.username)

class Group(models.Model):
    name = models.CharField(max_length=300)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    members = models.ManyToManyField(Profile, related_name='groups', blank=True)

    def __str__(self):
        return '%s' % (self.name)