from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import Condition, RiskScore, Population
from ..tasks import send_registration_email_to_user
from ..permissions import IsRegistered
from ..serializers import RiskScoreSerializer, ConditionSerializer, \
    PopulationSerializer


class ConditionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ Conditions are a possible beneficial or detremental set of symptoms or
    afflictions that are caused by (and also possibly mitigated by genetic
    variants.

    This endpoint provides a read-only way to access the global list of
    conditions as well as a list of possible risk reductors for that condition.

    list:
    The list of all conditions and their associated risk reductors.

    retrieve:
    Get a single condition and its risk reductors by the condition {id}.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Condition.objects.all().order_by('-name')
    serializer_class = ConditionSerializer


class PopulationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ Risk Scores are calculted relative to the user's determined ancestry.
    This ancestry is determined as a percentage of the user's similarity to the
    given populations. There is also a "custom" population which is user specific
    and reflects the user's combined ancestry.

    list:
    A list of all of the super populations, against which a user's ancestry is
    calculated.

    retrieve:
    A single population given by its {id}.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Population.objects.all().order_by('-name')
    serializer_class = PopulationSerializer


class RiskScoreViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ Risk scores are the user's given genetic risk, and other adjusted baseline
    risks for a given condition relative to a population. Each risk score also
    has a series of adjusted risk scores that can be used to visualized the
    effect of different lifestyle changes and how they affect the user's risk.

    list:
    A list of all of the given risk scores. Conditions without risk scores are
    assumed to not be ready for the user.

    retrieve:
    Get a single risk score by its {id}.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskScore.objects.all().order_by('-user')
    serializer_class = RiskScoreSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id','name', 'condition__id', 'condition__name']


