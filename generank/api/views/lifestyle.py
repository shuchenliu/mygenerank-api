from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope

from .. import filters
from ..models import LifestyleMetricStatus
from ..permissions import IsActive
from ..serializers import LifestyleMetricStatusSerializer


class LifestyleMetricStatusViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ Lifestyle metric statuses contain the user's current lifestyle metrics
    as well as metadata about when said metrics were last updated.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsActive]
    queryset = LifestyleMetricStatus.objects.all().order_by('-metric')
    serializer_class = LifestyleMetricStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
