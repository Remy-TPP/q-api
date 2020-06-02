import enum

from apps.profiles.models import (FriendshipStatus)

class FRIENDSHIP_STATUS(enum.Enum):
    REQUESTED = FriendshipStatus.objects.get(name='REQUESTED')
    ACCEPTED = FriendshipStatus.objects.get(name='ACCEPTED')
    REJECTED = FriendshipStatus.objects.get(name='REJECTED')
