from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import LifestyleMetricStatus
from ..serializers import LifestyleMetricStatusSerializer


class LifestyleMetricStatusViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ A list of variou lifestyle metrics and how the user is measured within it. """
    authentication_classes = [OAuth2Authentication, IsAuthenticated]
    queryset = LifestyleMetricStatus.objects.all().order_by('-metric')
    serializer_class = LifestyleMetricStatusSerializer
