from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import detail_route

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from gene_pc_api.twentythreeandme.models import Profile, User, Genotype
from gene_pc_api.twentythreeandme.serializers import UserSerializer,\
    ProfileSerializer, GenotypeSerializer


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
