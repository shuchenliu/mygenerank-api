import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password

from rest_framework import viewsets, request, response, renderers
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, renderer_classes, \
    detail_route, permission_classes, authentication_classes
from rest_framework.renderers import TemplateHTMLRenderer

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope
from rest_condition import And, Or

from . import filters
from .models import User, Activity, ActivityStatus, ActivityAnswer, \
    Condition, RiskScore, Population, ConsentPDF, Signature
from .tasks import send_registration_email_to_user
from .permissions import IsRegistered
from .serializers import UserSerializer,\
    ActivityAnswerSerializer, RiskScoreSerializer, ActivitySerializer,\
    ConditionSerializer, ActivityStatusSerializer, PopulationSerializer, \
    ConsentPDFSerializer, SignatureSerializer

from ..twentythreeandme import models as ttm_models
from ..twentythreeandme.tasks import twentythreeandme_delayed_import_task


logger = logging.getLogger()


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    model = User

    def create(self, request, *args, **kwargs):
        try:
            validate_password(request.data.get('password'))
        except ValidationError as e:
            logger.error('User creation failed: password did not validate.')
            return Response({ 'message': '\n'.join(e.messages) }, 400)

        response = super().create(request, *args, **kwargs)

        # Prep to send email.
        user = User.objects.get(username=response.data['username'])
        url = reverse('api:user-register', kwargs={'pk': user.id})
        registration_url = request.build_absolute_uri(url)

        try:
            send_registration_email_to_user.delay(registration_url,
                user.registration_code, user.email)
        except Exception as e:
            logger.error('An exception occurred while creating user. %s' % e)
        return Response({
            'description': 'User created. Registration Needed'
        }, 201)


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
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
            logger.error('User registration failed: User did not exist.')
        return Response({'error': 'Invalid Registration Code'})


class SignatureViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Signature.objects.all().order_by('-user')
    serializer_class = SignatureSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ConsentPDFViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ConsentPDF.objects.all().order_by('-user')
    serializer_class = ConsentPDFSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ActivityAnswerViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ActivityAnswer.objects.all().order_by('-user')
    serializer_class = ActivityAnswerSerializer
    search_fields = ['user__id','question_identifier']
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ConditionViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Condition.objects.all().order_by('-name')
    serializer_class = ConditionSerializer


class PopulationViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Population.objects.all().order_by('-name')
    serializer_class = PopulationSerializer


class RiskScoreViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskScore.objects.all().order_by('-user')
    serializer_class = RiskScoreSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id','name', 'condition__id', 'condition__name']


class ActivityViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
@permission_classes([IsAuthenticated])
def import23andme(request):
    token = request.data.get('token', None)
    userid = request.data.get('user', None)
    profileid = request.data.get('profile', None)

    if not (token and userid and profileid):
        return response.Response({'status': 'missing parameter'}, status=400)

    # Start the delayed task to set the user
    twentythreeandme_delayed_import_task.delay(token, userid, profileid)
    logger.info('23andMe Import Started for user %s' % userid)

    return response.Response({'status':'all set'}, status=200)


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def about_page(request):
    return Response({}, template_name='about.html')
