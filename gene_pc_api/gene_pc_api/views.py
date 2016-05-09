from rest_framework import viewsets
from rest_framework.decorators import detail_route
from gene_pc_api.gene_pc_api import models as gpc_models
from gene_pc_api.gene_pc_api.serializers import UserSerializer,\
    PhenotypesSerializer, RiskScoresSerializer, ActivitiesSerializer

from gene_pc_api.twentythreeandme import models as ttm_models
from gene_pc_api.twentythreeandme.api_client import *
from django.core.exceptions import ObjectDoesNotExist
from gene_pc_api.twentythreeandme.tasks import twentythreeandme_import_task

from django.http import HttpResponse
#import logging

def import23andme(request):

    code = request.GET.get('code', '')
    try:
        token = get_token(code)
    except KeyError:
        return HttpResponse("<p>Error: Please try again later</p>")
    user_info = get_user_info(token)
    user_id = user_info['id']

    try:
        """ If a user_id exists already then just display that user """
        existing_user_ttm = ttm_models.User.objects.get(user_id__exact=user_id)
        gpc_id = existing_user_ttm.apiuserid
        existing_user_gpc = gpc_models.User.objects.get(id__exact=gpc_id)
        return HttpResponse(existing_user_gpc.id)

    except ObjectDoesNotExist:
        """ Create a new user and start the import tasks
        if the user doesn't exist """
        new_user =  twentythreeandme_import_task(user_info, token)
        return HttpResponse(new_user.id)

class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    queryset = gpc_models.User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

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
