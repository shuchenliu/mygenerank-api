from rest_framework import permissions


class IsRegistered(permissions.BasePermission):
    message = 'You must register before accessing this information.'

    def has_permission(self, request, view):
        return request.user.registered
