import django
from rest_framework import filters


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        try:
            return queryset.filter(user=request.user)
        except django.core.exceptions.FieldError:
            return queryset.filter(id=request.user.id)
