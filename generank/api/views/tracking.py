from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import utils
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import TrackedEvent
from ..serializers import TrackedEventSerializer
from ..permissions import IsActive


class TrackedEventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = [AllowAny]
    permission_classes = []
    serializer_class = TrackedEventSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super(TrackedEventViewSet, self).create(request, *args, **kwargs)
        except utils.IntegrityError:
            return Response({
                'error' : { 'message': 'Item already exists.' }
            }, status=400)
