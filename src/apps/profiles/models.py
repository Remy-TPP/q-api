from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class ProfileType(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return '%s' % (self.name)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    biography = models.CharField(max_length=240, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/%Y-%m-%d')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    profiletypes = models.ManyToManyField(ProfileType, related_name='profile')
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return '%s' % (self.user.username)

class Group(models.Model):
    name = models.CharField(max_length=300)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    members = models.ManyToManyField(Profile, related_name='groups', blank=True)

    def __str__(self):
        return '%s' % (self.name)