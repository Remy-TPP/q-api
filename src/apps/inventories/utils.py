from common.utils import get_object_or_none

from apps.inventories.models import PlaceMember


def get_place_or_default(profile, place_id=None):
    """
    Uses get() to return an place by its id.
    If profile doesn't have this place, it will return Profile's default place.

    profile must be a Profile.
    place_id is optional.
    """
    place_member = get_object_or_none(
        PlaceMember,
        member_id=profile.id,
        place_id=place_id
    )
    return place_member.place if place_member else get_object_or_none(PlaceMember, member_id=profile.id, is_the_default_one=True).place
