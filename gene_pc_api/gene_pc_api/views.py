from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, request, response, renderers
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, renderer_classes, detail_route

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope

from gene_pc_api.gene_pc_api import filters
from gene_pc_api.gene_pc_api import models as gpc_models
from gene_pc_api.gene_pc_api.serializers import UserSerializer,\
    ActivityAnswerSerializer, RiskScoreSerializer, ActivitySerializer,\
    ConditionSerializer, ActivityStatusSerializer, PopulationSerializer

from gene_pc_api.twentythreeandme import models as ttm_models
#import logging

class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    model = gpc_models.User


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)

    @detail_route(methods=['POST'], permission_classes=[IsAuthenticated])
    def register(self, request, pk):
        code = request.data.get('code', None)
        try:
            user = gpc_models.User.objects.get(id=pk, registration_code=code)
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        except ObjectDoesNotExist:
            pass
        return Response({'error': 'Invalid Registration Code'})


class ActivityAnswerViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.ActivityAnswer.objects.all().order_by('-user')
    serializer_class = ActivityAnswerSerializer
    search_fields = ['user__id','question_identifier']
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ConditionViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.Condition.objects.all().order_by('-name')
    serializer_class = ConditionSerializer


class PopulationViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.Population.objects.all().order_by('-name')
    serializer_class = PopulationSerializer


class RiskScoreViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.RiskScore.objects.all().order_by('-user')
    serializer_class = RiskScoreSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id','name', 'condition__id', 'condition__name']


class ActivityViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = gpc_models.ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']


@api_view(['POST'])
@renderer_classes((renderers.StaticHTMLRenderer,))
def import23andme(request):
    code = request.data.get('code', None)
    if not code:
        return response.Response(None, status=400)
    # TODO: Kick off import.
    return response.Response({code: code}, template_name='authentication_response.html')
