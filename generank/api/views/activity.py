import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import User, Activity, ActivityStatus, ActivityAnswer
from ..serializers import ActivityAnswerSerializer, ActivitySerializer, \
    ActivityStatusSerializer

logger = logging.getLogger()


class ActivityViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activities to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityAnswerViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activity answers to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ActivityAnswer.objects.all().order_by('-user')
    serializer_class = ActivityAnswerSerializer
    search_fields = ['user__id','question_identifier']
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ActivityStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activity statuses to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']

