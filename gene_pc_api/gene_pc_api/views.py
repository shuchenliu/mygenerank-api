from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, request, response, renderers
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, renderer_classes, detail_route

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope

from . import filters
from .models import User, Activity, ActivityStatus, ActivityAnswer, \
    Condition, RiskScore, Population
from .tasks import send_registration_email_to_user
from .permissions import IsRegistered
from .serializers import UserSerializer,\
    ActivityAnswerSerializer, RiskScoreSerializer, ActivitySerializer,\
    ConditionSerializer, ActivityStatusSerializer, PopulationSerializer

from gene_pc_api.twentythreeandme import models as ttm_models
from gene_pc_api.twentythreeandme.tasks import twentythreeandme_delayed_import_task


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    model = User

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        user = User.objects.get(username=response.data['username'])
        send_registration_email_to_user.delay(request, user)
        return Response(
            {'description': 'User created. Registration Needed'}, 201)


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)

    @detail_route(methods=['GET'], permission_classes=[])
    def register(self, request, pk):
        code = request.query_params.get('code', None)
        try:
            user = User.objects.get(id=pk, registration_code=code)
            user.registered = True
            user.save()
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        except ObjectDoesNotExist:
            pass
        return Response({'error': 'Invalid Registration Code'})


class ActivityAnswerViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = ActivityAnswer.objects.all().order_by('-user')
    serializer_class = ActivityAnswerSerializer
    search_fields = ['user__id','question_identifier']
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ConditionViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = Condition.objects.all().order_by('-name')
    serializer_class = ConditionSerializer


class PopulationViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = Population.objects.all().order_by('-name')
    serializer_class = PopulationSerializer


class RiskScoreViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = RiskScore.objects.all().order_by('-user')
    serializer_class = RiskScoreSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id','name', 'condition__id', 'condition__name']


class ActivityViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated, IsRegistered]
    queryset = ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']


@api_view(['POST'])
def import23andme(request):
    token = request.data.get('token', None)
    userid = request.data.get('user', None)
    profileid = request.data.get('profile', None)
    if not (token and userid and profileid):
        return response.Response({'status':"missing parameter"}, status=400)

    ''' Start the delayed task to set the user '''
    twentythreeandme_delayed_import_task.delay(token, userid, profileid)
    return response.Response({'status':'all set'}, status=200)
