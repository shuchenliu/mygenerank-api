from rest_framework import permissions


class IsRegistered(permissions.BasePermission):
    message = 'You must register before accessing this information.'

    def has_permission(self, request, view):
        try:
            return request.user.registered
        except AttributeError:
            return False

class IsActive(permissions.BasePermission):
    message = 'This account is inactive.'

    def has_permission(self, request, view):
        try:
            return request.user.is_active
        except AttributeError:
            return False
