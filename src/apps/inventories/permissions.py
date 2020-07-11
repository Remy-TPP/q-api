from rest_framework import permissions


class IsMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        profile = request.user.profile

        return profile in obj.members.all()
