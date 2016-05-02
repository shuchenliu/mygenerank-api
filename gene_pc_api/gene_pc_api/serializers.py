from rest_framework import serializers

from .models import Phenotypes, User, RiskScores, Activities

class UserSerializer(serializers.HyperlinkedModelSerializer):
    phenotypes = serializers.HyperlinkedRelatedField(
            view_name='api:phenotypes-detail',
            many=True,
            read_only=True
        )

    risk_scores = serializers.HyperlinkedRelatedField(
            view_name='api:riskscores-detail',
            many=True,
            read_only=True
        )

    activities = serializers.HyperlinkedRelatedField(
                view_name='api:activities-detail',
                many=True,
                read_only=True
            )


    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'phenotypes', 'risk_scores',
            'profile_id', 'auth_code', 'user_id', 'activities')
        write_only_fields = ('auth_code',)
        extra_kwargs = {'url': {'view_name': 'api:user-detail'}}


class PhenotypesSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = Phenotypes
        fields = ('user', 'name', 'value', 'description', 'datatype')
        extra_kwargs = {'url': {'view_name': 'api:phenotypes-detail'}}


class RiskScoresSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = RiskScores
        fields = ('user', 'name', 'value', 'description', 'datatype', 'calculated')
        extra_kwargs = {'url': {'view_name': 'api:riskscores-detail'}}



class ActivitiesSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = Activities
        fields = ('user', 'name', 'subtitle', 'complete')
        extra_kwargs = {'url': {'view_name': 'api:activities-detail'}}
