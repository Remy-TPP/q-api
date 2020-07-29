from rest_framework import permissions


class UpdateOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        return request.method not in ['PUT', 'PATCH'] or user_editing == user_edited


class DestroyOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        return request.method not in ['DELETE'] or user_editing == user_edited


class IsOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user_editing = request.user.id
        user_edited = obj.user_id

        return request.method not in ['POST'] or user_editing == user_edited
