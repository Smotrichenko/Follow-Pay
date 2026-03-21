from rest_framework import permissions


class IsCreatorOwner(permissions.BasePermission):
    """Разрешаем редактировать/публиковать пост только автору"""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.creator.user_id == request.user_id
