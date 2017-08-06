from rest_framework import viewsets, request, response, renderers
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view, renderer_classes, \
    detail_route, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .models import Profile, User, Genotype, APIToken, Settings
from .tasks import import_account

from .serializers import UserSerializer,\
    ProfileSerializer, GenotypeSerializer, SettingsSerializer


class SettingsViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all().order_by('-user')
    serializer_class = ProfileSerializer


class GenotypeViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAdminUser]
    queryset = Genotype.objects.all().order_by('-profile')
    serializer_class = GenotypeSerializer


@api_view(['POST'])
@authentication_classes([OAuth2Authentication])
@permission_classes([IsAuthenticated])
def import_data(request):
    token = request.data['token']
    user_id = request.data['user']
    profile_id = request.data['profile']

    import_account.delay(token, user_id, profile_id)

    return response.Response({'status':'all set'}, status=200)
