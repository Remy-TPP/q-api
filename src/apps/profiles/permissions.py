from rest_framework import permissions

class UpdateOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        if request.method in ['PUT', 'PATCH'] and user_editing != user_edited:
            return False
        else:
            return True

class DestroyOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        if request.method in ['DELETE'] and user_editing != user_edited:
            return False
        else:
            return True

class IsOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        if request.method in ['POST'] and user_editing != user_edited:
            return False
        else:
            return True
