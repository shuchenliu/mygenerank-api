from rest_framework import viewsets
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import Condition, RiskScore, Population
from ..tasks import send_registration_email_to_user
from ..permissions import IsRegistered
from ..serializers import RiskScoreSerializer, ConditionSerializer, \
    PopulationSerializer


class ConditionViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Condition.objects.all().order_by('-name')
    serializer_class = ConditionSerializer


class PopulationViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows populations to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Population.objects.all().order_by('-name')
    serializer_class = PopulationSerializer


class RiskScoreViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows risk scores to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskScore.objects.all().order_by('-user')
    serializer_class = RiskScoreSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id','name', 'condition__id', 'condition__name']
