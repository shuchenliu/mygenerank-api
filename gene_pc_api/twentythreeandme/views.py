from rest_framework import viewsets
from rest_framework.decorators import detail_route
from gene_pc_api.twentythreeandme.models import Profile, User, Genotype
from gene_pc_api.twentythreeandme.serializers import UserSerializer,\
    ProfileSerializer, GenotypeSerializer



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('-user')
    serializer_class = ProfileSerializer


class GenotypeViewSet(viewsets.ModelViewSet):
    queryset = Genotype.objects.all().order_by('-profile')
    serializer_class = GenotypeSerializer
