from rest_framework import viewsets
from gene_pc_api.twentythreeandme.models import Profile, User, Genome
from gene_pc_api.twentythreeandme.serializers import UserSerializer,\
    ProfileSerializer, GenomeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('-user')
    serializer_class = ProfileSerializer


class GenomeViewSet(viewsets.ModelViewSet):
    queryset = Genome.objects.all().order_by('-profile')
    serializer_class = GenomeSerializer
