from rest_framework import viewsets
from rest_framework.decorators import detail_route
from gene_pc_api.gene_pc_api import models as gpc_models
from gene_pc_api.gene_pc_api.serializers import UserSerializer,\
    PhenotypesSerializer, RiskScoresSerializer, ActivitiesSerializer

from gene_pc_api.twentythreeandme import models as ttm_models
from gene_pc_api.twentythreeandme.api_client import *
from django.core.exceptions import ObjectDoesNotExist
from gene_pc_api.twentythreeandme.tasks import twentythreeandme_import_task

class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = gpc_models.User.objects.all().order_by('-date_joined')

    serializer_class = UserSerializer

    @detail_route(methods=['get'])
    def import23andme(self, request, code):

        token = get_token(code)
        user_info = get_user_info(token)
        user_id = user_info['id']

        try:
            """ If a user_id exists already then just display that user """
            existing_user = ttm_models.User.objects.get(user_id__exact=user_id)

        except ObjectDoesNotExist:
            """ Create a new user and start the import tasks
            if the user doesn't exist """
            new_user =  twentythreeandme_import_task(user_info, token)

        return new_user



class PhenotypesViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = gpc_models.Phenotypes.objects.all().order_by('-user')
    serializer_class = PhenotypesSerializer


class RiskScoresViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = gpc_models.RiskScores.objects.all().order_by('-user')
    serializer_class = RiskScoresSerializer

class ActivitiesViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = gpc_models.Activities.objects.all().order_by('-user')
    serializer_class = ActivitiesSerializer
