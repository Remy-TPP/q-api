from django.db import models
from django.conf import settings
from rest_framework.serializers import ValidationError


class ProfileType(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return '%s' % (self.name)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name="profile")
    biography = models.CharField(max_length=240, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/%Y-%m-%d')
    updated_at = models.DateTimeField(auto_now=True)

    profiletypes = models.ManyToManyField(ProfileType, related_name='profile')
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return '%s' % (self.user.username)


class FriendshipStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, primary_key=True)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name_plural = "friendship statuses"


class FriendshipRequest(models.Model):
    profile_requesting = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='profile_requesting')

    profile_requested = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='profile_requested')

    status = models.ForeignKey(FriendshipStatus, on_delete=models.CASCADE)


class Event(models.Model):
    from apps.inventories.models import Place

    name = models.CharField(max_length=300, blank=True, null=True)

    starting_datetime = models.DateTimeField()
    finishing_datetime = models.DateTimeField()

    only_host_inventory = models.BooleanField(default=True)
    host = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='hosted_events')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, blank=True, null=False)

    attendees = models.ManyToManyField(Profile, related_name='events', blank=True)

    def __str__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        from apps.inventories.utils import get_place_or_default

        if not self.place_id:
            place = get_place_or_default(self.host)
            if not place:
                raise ValidationError('Please, create a place first!')
            self.place = place
        super(Event, self).save(*args, **kwargs)
