from rest_framework import serializers

from .models import Genome, Profile, User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profiles = serializers.HyperlinkedRelatedField(
            view_name='twentythreeandme:profile-detail',
            many=True,
            read_only=True
        )

    class Meta:
        model = User
        fields = ('url', 'user_id', 'email', 'profiles', 'token')
        extra_kwargs = {'url': {'view_name': 'twentythreeandme:user-detail'}}


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='twentythreeandme:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = Profile
        fields = ('url', 'user', 'profile_id', 'genotyped', 'genome')
        extra_kwargs = {'url': {'view_name': 'twentythreeandme:profile-detail'}}


class GenomeSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
            view_name='twentythreeandme:genome-detail',
            many=False,
            queryset=Profile.objects.all()
        )

    class Meta:
        model = Genome
        fields = ('url', 'profile', 'genome_file_url')
        extra_kwargs = {'url': {'view_name': 'twentythreeandme:genome-detail'}}
