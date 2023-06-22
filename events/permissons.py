from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
    message = "권한이 없습니다"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_admin


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = "권한이 없습니다"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
