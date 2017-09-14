import uuid

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework import viewsets, request, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import detail_route, api_view
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.authentication import SessionAuthentication

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope

from .. import filters
from ..models import User, Activity, ActivityStatus, ActivityAnswer, \
    Condition, RiskScore, Population, ConsentPDF, Signature, HealthSample
from ..tasks import send_registration_email_to_user
from ..permissions import IsRegistered
from ..serializers import UserSerializer, ConsentPDFSerializer, \
    SignatureSerializer


class CreateUserView(CreateAPIView):
    exclude_from_schema = True
    serializer_class = UserSerializer
    model = User

    def create(self, request, *args, **kwargs):
        try:
            validate_password(request.POST['password'])
        except ValidationError as e:
            return Response({ 'message': '\n'.join(e.messages) }, 400)
        except MultiValueDictKeyError:
            return Response({ 'message': 'Password is required'}, 400)

        try:
            username=request.POST['username']
        except MultiValueDictKeyError:
            return Response({ 'message': 'Username is required'}, 400)

        try:
            EmailValidator()(username)
        except ValidationError:
            return Response({ 'message': 'Username must be a valid email address'}, 400)

        try:
            User.objects.get(username=username)
            return Response({ 'message': 'User already exists' }, 400)
        except ObjectDoesNotExist:
            pass

        response = super().create(request, *args, **kwargs)

        # Prep to send email.
        user = User.objects.get(username=response.data['username'])
        url = reverse('user-register', kwargs={'pk': user.id})
        registration_url = request.build_absolute_uri(url)

        try:
            send_registration_email_to_user.delay(registration_url,
                user.registration_code, user.email)
        except Exception as e:
            print('Error sending mail', e)
        return Response({
            'description': 'User created. Registration Needed'
        }, 201)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ API endpoint that allows users to be viewed or edited. """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)

    @detail_route(methods=['GET'], permission_classes=[], renderer_classes=(TemplateHTMLRenderer,), exclude_from_schema = True)
    def register(self, request, pk):
        code = request.query_params.get('code', None)
        try:
            user = User.objects.get(id=pk, registration_code=code)
            user.registered = True
            user.save()
            return Response({}, template_name='confirm_registration.html')
        except ObjectDoesNotExist as e:
            print('User registration failed:', e)

        return Response({'error': 'Invalid Registration Code'}, 400,
            template_name='confirm_registration.html')

    def destroy(self, request, pk, *args, **kwargs):
        user = get_object_or_404(self.queryset, pk=pk)
        user.is_active = False
        user.username = '_inactive_%s' % str(uuid.uuid4().hex)[:20]
        user.save()
        return Response(None, 204)


class SignatureViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows signatures to be viewed or edited. """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Signature.objects.all().order_by('-consent_pdf')
    serializer_class = SignatureSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    exclude_from_schema = True


class ConsentPDFViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows consent pdfs to be viewed or edited. """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ConsentPDF.objects.all().order_by('-user')
    serializer_class = ConsentPDFSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    exclude_from_schema = True
