from rest_framework import viewsets
from gene_pc_api.gene_pc_api.models import Phenotypes, User,\
    RiskScores, Activities
from gene_pc_api.gene_pc_api.serializers import UserSerializer,\
    PhenotypesSerializer, RiskScoresSerializer, ActivitiesSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PhenotypesViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = Phenotypes.objects.all().order_by('-user')
    serializer_class = PhenotypesSerializer


class RiskScoresViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = RiskScores.objects.all().order_by('-user')
    serializer_class = RiskScoresSerializer

class ActivitiesViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = Activities.objects.all().order_by('-user')
    serializer_class = ActivitiesSerializer
