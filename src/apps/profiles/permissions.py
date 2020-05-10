import json
from rest_framework import permissions

class UpdateDestroyOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        if request.method in ['PUT', 'PATCH', 'DELETE'] and user_editing!=user_edited:
            return False
        else:
            return True
        