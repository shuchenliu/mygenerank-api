import logging, uuid

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, request, response, renderers, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, renderer_classes, \
    detail_route, permission_classes, authentication_classes
from rest_framework.renderers import TemplateHTMLRenderer

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope
from rest_condition import And, Or

from . import filters
from .models import User, Activity, ActivityStatus, ActivityAnswer, \
    Condition, RiskScore, Population, ConsentPDF, Signature, HealthSample
from .tasks import send_registration_email_to_user
from .permissions import IsRegistered
from .serializers import UserSerializer,\
    ActivityAnswerSerializer, RiskScoreSerializer, ActivitySerializer,\
    ConditionSerializer, ActivityStatusSerializer, PopulationSerializer, \
    ConsentPDFSerializer, SignatureSerializer, HealthSampleSerializer


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

        try:
            User.objects.get(username=request.data.get('username'))
            logger.error('User creation failed: user already exists.')
            return Response({ 'message': 'User already exists' }, 400)
        except ObjectDoesNotExist:
            pass

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


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)

    @detail_route(methods=['GET'], permission_classes=[], renderer_classes=(TemplateHTMLRenderer,))
    def register(self, request, pk):
        code = request.query_params.get('code', None)
        try:
            user = User.objects.get(id=pk, registration_code=code)
            user.registered = True
            user.save()
            return Response({}, template_name='confirm_registration.html')
        except ObjectDoesNotExist:
            logger.error('User registration failed: User did not exist.')

        return Response({'error': 'Invalid Registration Code'},
            template_name='confirm_registration.html')

    def destroy(self, request, pk, *args, **kwargs):
        user = get_object_or_404(self.queryset, pk=pk)
        user.is_active = False
        user.username = '_inactive_%s' % str(uuid.uuid4().hex)[:20]
        user.save()
        return Response(None, 204)


class SignatureViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows signatures to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Signature.objects.all().order_by('-user')
    serializer_class = SignatureSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ConsentPDFViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows consent pdfs to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ConsentPDF.objects.all().order_by('-user')
    serializer_class = ConsentPDFSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ActivityAnswerViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activity answers to be viewed or edited. """
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


class ActivityViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activities to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityStatusViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activity statuses to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']


class HealthSampleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ API endpoint that allows health samples to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = HealthSample.objects.all().order_by('-end_date')
    serializer_class = HealthSampleSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'identifier', 'start_date', 'end_date']

    def create(self, request, *args, **kwargs):
        """ Override allows for bulk upload due to heavy volume of requests.
        source: http://stackoverflow.com/questions/37329771/django-rest-bulk-post-post-array-of-json-objects#37332640
        """
        try:
            data = request.data['objects']
        except KeyError:
            data = request.data

        is_many = True if isinstance(data, list) else False
        serializer = self.get_serializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({}, status=201)

    def get(self, request, *args, **kwargs):
        """ A simple API that returns the date of the last health sample that
        has been uploaded for the given user.
        """
        queryset = self.filter_queryset(self.get_queryset())
        if len(queryset) == 0:
            return Response(None, status=404)
        last = queryset[0]
        return Response({
            'end_date': last.end_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'identifier': last.identifier
        }, status=200)


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def about_page(request):
    return Response({}, template_name='about.html')
