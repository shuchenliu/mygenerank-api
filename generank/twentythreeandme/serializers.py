from rest_framework import serializers

from .models import Genotype, Profile, User


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
    genotype = serializers.HyperlinkedRelatedField(
            view_name='twentythreeandme:genotype-detail',
            many=False,
            queryset=Genotype.objects.all()
        )

    class Meta:
        model = Profile
        fields = ('url', 'user', 'profile_id', 'genotyped', 'genotype')
        extra_kwargs = {'url': {'view_name': 'twentythreeandme:profile-detail'}}


class GenotypeSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
            view_name='twentythreeandme:profile-detail',
            many=False,
            queryset=Profile.objects.all()
        )

    class Meta:
        model = Genotype
        fields = ('url', 'profile', 'genotype_file', 'converted_file')
        extra_kwargs = {'url': {'view_name': 'twentythreeandme:genotype-detail'}}
