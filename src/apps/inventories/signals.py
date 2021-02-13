from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.inventories.models import PlaceMember


@receiver(m2m_changed, sender=PlaceMember)
def create_place_member(action, instance, pk_set, **_kwargs):
    if action == 'post_add':
        for member_id in pk_set:
            if not PlaceMember.objects.filter(member_id=member_id, is_the_default_one=True).exists():
                PlaceMember.objects.filter(member_id=member_id, place=instance).update(is_the_default_one=True)
    if action == 'post_remove':
        for member_id in pk_set:
            if not PlaceMember.objects.filter(member_id=member_id, is_the_default_one=True).exists():
                placemember = PlaceMember.objects.filter(member_id=member_id).first()
                if placemember:
                    placemember.is_the_default_one = True
                    placemember.save()
