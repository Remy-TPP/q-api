

def get_place_or_default(profile, place_id):
    """
    Uses get() to return an place by its id.
    If profile is None or doesn't have this place, it will return Profile's default place.

    profile may be a Profile.
    place_id is optional.
    """
    queryset = profile.places.all()
    try:
        return queryset.get(id=place_id)
    except queryset.model.DoesNotExist:
        # TODO: por ahora devuelve el primero, pero debe devolver el default
        return queryset.first()
